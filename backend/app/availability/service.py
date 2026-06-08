"""Servicio de disponibilidad integrada."""

from datetime import date as date_type, datetime, time, timedelta

from sqlalchemy import or_

from app import db
from app.calendar.models import InstitutionalEvent, WorkCalendarDay, WorkSchedule
from app.meetings.models import InvitationStatus, Meeting, MeetingParticipant, MeetingStatus
from app.roles.models import RoleSlug
from app.rooms.models import Room
from app.settings.service import SettingsService
from app.users.models import User


class AvailabilityStatus:
    AVAILABLE = "available"
    BUSY = "busy"
    PENDING = "pending"
    REJECTED = "rejected"
    CREATOR_BLOCKED = "creator_blocked"
    OUTSIDE_WORK_HOURS = "outside_work_hours"
    NON_WORKING_DAY = "non_working_day"


class AvailabilityService:
    @staticmethod
    def check(data: dict, creator_id: int | None = None, exclude_meeting_id: int | None = None) -> dict:
        meeting_date = data["date"]
        start_time = data["start_time"]
        end_time = data["end_time"]
        room_id = data.get("room_id")
        participant_ids = list(dict.fromkeys(data.get("participant_ids") or []))

        hard_blocks: list[dict] = []
        warnings: list[dict] = []

        if start_time >= end_time:
            hard_blocks.append({"code": "INVALID_TIME_RANGE", "message": "La hora de inicio debe ser menor que la hora de fin."})

        settings = AvailabilityService._settings()
        duration_minutes = AvailabilityService._duration_minutes(start_time, end_time)
        if duration_minutes > settings["max_meeting_duration_minutes"]:
            hard_blocks.append({"code": "MAX_DURATION_EXCEEDED", "message": "La duración excede el máximo permitido."})

        starts_at = datetime.combine(meeting_date, start_time)
        min_start = datetime.now() + timedelta(minutes=settings["min_meeting_notice_minutes"])
        if starts_at < min_start:
            hard_blocks.append({"code": "MIN_NOTICE_NOT_MET", "message": "No cumple la anticipación mínima configurada."})

        if len(participant_ids) > settings["max_meeting_participants"]:
            hard_blocks.append({"code": "MAX_PARTICIPANTS_EXCEEDED", "message": "Se excede el máximo de participantes."})

        AvailabilityService._validate_working_time(meeting_date, start_time, end_time, settings, hard_blocks)
        AvailabilityService._validate_institutional_events(meeting_date, start_time, end_time, hard_blocks)

        room_payload = None
        if room_id:
            room_payload = AvailabilityService._room_status(room_id, meeting_date, start_time, end_time, len(participant_ids), exclude_meeting_id)
            if not room_payload["available"]:
                hard_blocks.extend(room_payload["hard_blocks"])
            warnings.extend(room_payload["warnings"])

        if creator_id:
            creator_conflicts = AvailabilityService.user_blocking_conflicts(creator_id, meeting_date, start_time, end_time, exclude_meeting_id)
            if creator_conflicts:
                hard_blocks.append({
                    "code": "CREATOR_BUSY",
                    "message": "El creador ya tiene una reunión en ese horario.",
                    "conflicts": creator_conflicts,
                })

        participants = []
        for user_id in participant_ids:
            participant = AvailabilityService._participant_status(user_id, meeting_date, start_time, end_time, exclude_meeting_id)
            participants.append(participant)
            if participant["hard_block"]:
                hard_blocks.append({"code": participant["hard_block"], "message": participant["message"], "user_id": user_id})
            elif participant["status"] in (AvailabilityStatus.BUSY, AvailabilityStatus.PENDING):
                warnings.append({"code": f"PARTICIPANT_{participant['status'].upper()}", "user_id": user_id, "message": participant["message"]})

        return {
            "can_create": not hard_blocks,
            "hard_blocks": hard_blocks,
            "warnings": warnings,
            "room": room_payload,
            "participants": participants,
            "suggested_slots": [],
        }

    @staticmethod
    def user_blocking_conflicts(user_id: int, meeting_date: date_type, start_time: time, end_time: time, exclude_meeting_id: int | None = None) -> list[dict]:
        query = Meeting.query.filter(
            Meeting.date == meeting_date,
            Meeting.status != MeetingStatus.CANCELLED,
            Meeting.start_time < end_time,
            Meeting.end_time > start_time,
        )
        if exclude_meeting_id:
            query = query.filter(Meeting.id != exclude_meeting_id)

        creator_conflicts = query.filter(Meeting.created_by_user_id == user_id).all()
        accepted_conflicts = (
            query.join(MeetingParticipant)
            .filter(MeetingParticipant.user_id == user_id, MeetingParticipant.invitation_status == InvitationStatus.ACCEPTED)
            .all()
        )
        return [AvailabilityService._meeting_conflict(m, "creator") for m in creator_conflicts] + [
            AvailabilityService._meeting_conflict(m, "accepted") for m in accepted_conflicts
        ]

    @staticmethod
    def _participant_status(user_id: int, meeting_date: date_type, start_time: time, end_time: time, exclude_meeting_id: int | None) -> dict:
        user = db.session.get(User, user_id)
        if not user:
            return AvailabilityService._participant_payload(user_id, None, AvailabilityStatus.BUSY, [], "Usuario no encontrado.", "USER_NOT_FOUND")
        if not user.is_active:
            return AvailabilityService._participant_payload(user_id, user, AvailabilityStatus.BUSY, [], "Usuario inactivo.", "USER_INACTIVE")
        if user.role and user.role.slug == RoleSlug.ADMIN:
            return AvailabilityService._participant_payload(user_id, user, AvailabilityStatus.BUSY, [], "Admin no puede participar en reuniones.", "ADMIN_PARTICIPANT_NOT_ALLOWED")

        conflicts = AvailabilityService.user_blocking_conflicts(user_id, meeting_date, start_time, end_time, exclude_meeting_id)
        if conflicts:
            return AvailabilityService._participant_payload(user_id, user, AvailabilityStatus.BUSY, conflicts, "Participante ocupado.", None)

        pending = AvailabilityService._participant_invitation_conflicts(user_id, meeting_date, start_time, end_time, InvitationStatus.PENDING, exclude_meeting_id)
        if pending:
            return AvailabilityService._participant_payload(user_id, user, AvailabilityStatus.PENDING, pending, "Participante con invitación pendiente.", None)

        rejected = AvailabilityService._participant_invitation_conflicts(user_id, meeting_date, start_time, end_time, InvitationStatus.REJECTED, exclude_meeting_id)
        if rejected:
            return AvailabilityService._participant_payload(user_id, user, AvailabilityStatus.REJECTED, rejected, "Participante rechazó invitación en ese horario.", None)

        return AvailabilityService._participant_payload(user_id, user, AvailabilityStatus.AVAILABLE, [], "Disponible.", None)

    @staticmethod
    def _participant_invitation_conflicts(user_id: int, meeting_date: date_type, start_time: time, end_time: time, status: str, exclude_meeting_id: int | None) -> list[dict]:
        query = (
            Meeting.query.join(MeetingParticipant)
            .filter(
                Meeting.date == meeting_date,
                Meeting.status != MeetingStatus.CANCELLED,
                Meeting.start_time < end_time,
                Meeting.end_time > start_time,
                MeetingParticipant.user_id == user_id,
                MeetingParticipant.invitation_status == status,
            )
        )
        if exclude_meeting_id:
            query = query.filter(Meeting.id != exclude_meeting_id)
        return [AvailabilityService._meeting_conflict(meeting, status) for meeting in query.all()]

    @staticmethod
    def _room_status(room_id: int, meeting_date: date_type, start_time: time, end_time: time, participant_count: int, exclude_meeting_id: int | None) -> dict:
        room = db.session.get(Room, room_id)
        hard_blocks = []
        warnings = []
        if not room:
            return {"id": room_id, "name": None, "available": False, "conflicts": [], "hard_blocks": [{"code": "ROOM_NOT_FOUND", "message": "Sala no encontrada."}], "warnings": []}
        if not room.is_active:
            hard_blocks.append({"code": "ROOM_INACTIVE", "message": "Sala inactiva."})

        conflicts_query = Meeting.query.filter(
            Meeting.room_id == room_id,
            Meeting.date == meeting_date,
            Meeting.status != MeetingStatus.CANCELLED,
            Meeting.start_time < end_time,
            Meeting.end_time > start_time,
        )
        if exclude_meeting_id:
            conflicts_query = conflicts_query.filter(Meeting.id != exclude_meeting_id)
        conflicts = [AvailabilityService._meeting_conflict(meeting, "room") for meeting in conflicts_query.all()]
        if conflicts:
            hard_blocks.append({"code": "ROOM_BUSY", "message": "Sala ocupada.", "conflicts": conflicts})
        if participant_count > room.capacity:
            warnings.append({"code": "ROOM_CAPACITY_EXCEEDED", "message": "La cantidad de invitados supera la capacidad de la sala."})

        return {
            "id": room.id,
            "name": room.name,
            "available": not hard_blocks,
            "conflicts": conflicts,
            "hard_blocks": hard_blocks,
            "warnings": warnings,
        }

    @staticmethod
    def _validate_working_time(meeting_date: date_type, start_time: time, end_time: time, settings: dict, hard_blocks: list[dict]):
        calendar_day = WorkCalendarDay.query.filter_by(date=meeting_date).first()
        if calendar_day and not calendar_day.is_working_day and calendar_day.blocks_meetings:
            hard_blocks.append({"code": "NON_WORKING_DAY", "message": "Día no laborable bloqueante."})
            return

        schedule = WorkSchedule.query.filter_by(weekday=meeting_date.isoweekday()).first()
        if not schedule:
            return
        if not schedule.is_working_day and not settings["allow_meetings_on_non_working_days"]:
            hard_blocks.append({"code": "NON_WORKING_DAY", "message": "Día no laborable."})
            return
        if schedule.is_working_day and not settings["allow_meetings_outside_work_hours"]:
            if not schedule.start_time or not schedule.end_time or start_time < schedule.start_time or end_time > schedule.end_time:
                hard_blocks.append({"code": "OUTSIDE_WORK_HOURS", "message": "Horario fuera de la jornada laboral."})

    @staticmethod
    def _validate_institutional_events(meeting_date: date_type, start_time: time, end_time: time, hard_blocks: list[dict]):
        events = InstitutionalEvent.query.filter(
            InstitutionalEvent.date == meeting_date,
            InstitutionalEvent.blocks_agenda.is_(True),
            or_(InstitutionalEvent.start_time.is_(None), InstitutionalEvent.start_time < end_time),
            or_(InstitutionalEvent.end_time.is_(None), InstitutionalEvent.end_time > start_time),
        ).all()
        for event in events:
            hard_blocks.append({"code": "INSTITUTIONAL_EVENT_BLOCK", "message": event.title, "event_id": event.id})

    @staticmethod
    def _settings() -> dict:
        SettingsService.seed_defaults()
        settings = {setting.key: setting.get_typed_value() for setting in SettingsService.list_settings()}
        return {
            "max_meeting_participants": settings.get("max_meeting_participants", 20),
            "max_meeting_duration_minutes": settings.get("max_meeting_duration_minutes", 240),
            "min_meeting_notice_minutes": settings.get("min_meeting_notice_minutes", 60),
            "allow_meetings_outside_work_hours": settings.get("allow_meetings_outside_work_hours", False),
            "allow_meetings_on_non_working_days": settings.get("allow_meetings_on_non_working_days", False),
        }

    @staticmethod
    def _duration_minutes(start_time: time, end_time: time) -> int:
        start = datetime.combine(date_type.today(), start_time)
        end = datetime.combine(date_type.today(), end_time)
        return int((end - start).total_seconds() // 60)

    @staticmethod
    def _meeting_conflict(meeting: Meeting, reason: str) -> dict:
        return {
            "id": meeting.id,
            "title": meeting.title,
            "date": meeting.date.isoformat(),
            "start_time": meeting.start_time.strftime("%H:%M"),
            "end_time": meeting.end_time.strftime("%H:%M"),
            "reason": reason,
        }

    @staticmethod
    def _participant_payload(user_id: int, user: User | None, status: str, conflicts: list[dict], message: str, hard_block: str | None) -> dict:
        return {
            "id": user_id,
            "full_name": user.full_name if user else None,
            "status": status,
            "conflicts": conflicts,
            "message": message,
            "hard_block": hard_block,
        }
