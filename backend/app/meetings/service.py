"""Servicios de reuniones e invitaciones."""

from datetime import datetime, timezone

from app import db
from app.audit.service import AuditEvent, AuditService
from app.availability.service import AvailabilityService
from app.meetings.models import InvitationStatus, Meeting, MeetingModality, MeetingParticipant, MeetingStatus
from app.notifications.service import NotificationEvent, NotificationService
from app.roles.models import RoleSlug
from app.users.models import User


class MeetingService:
    MODALITY_MAP = {
        "presencial": MeetingModality.IN_PERSON,
        "in_person": MeetingModality.IN_PERSON,
        "virtual": MeetingModality.VIRTUAL,
        "hibrida": MeetingModality.HYBRID,
        "hybrid": MeetingModality.HYBRID,
    }

    @staticmethod
    def create_meeting(creator: User, data: dict) -> tuple[Meeting | None, dict | None]:
        MeetingService._ensure_can_operate_meetings(creator, allow_secretary=True)
        participant_ids = data["participant_ids"]
        if len(participant_ids) != len(set(participant_ids)):
            participant_ids = list(set([int(pid) for pid in data.get("participant_ids", []) if pid]))
        if not participant_ids:
            raise ValueError("Debe seleccionar al menos un participante.")

        modality = MeetingService._normalize_modality(data["modality"])
        if modality in (MeetingModality.IN_PERSON, MeetingModality.HYBRID) and not data.get("room_id"):
            raise ValueError("room_id es obligatorio para reuniones presenciales o híbridas.")

        availability = AvailabilityService.check(
            {
                "date": data["date"],
                "start_time": data["start_time"],
                "end_time": data["end_time"],
                "room_id": data.get("room_id"),
                "participant_ids": participant_ids,
            },
            creator_id=creator.id,
        )
        if availability["hard_blocks"]:
            return None, availability

        meeting = Meeting(
            title=data["title"].strip(),
            objective=data["objective"].strip(),
            agenda_items=data["agenda_items"],
            description=data.get("description"),
            date=data["date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            modality=modality,
            room_id=data.get("room_id"),
            virtual_link=data.get("virtual_link"),
            created_by_user_id=creator.id,
            status=MeetingStatus.SCHEDULED,
        )
        db.session.add(meeting)
        db.session.flush()

        for participant_id in participant_ids:
            db.session.add(MeetingParticipant(meeting_id=meeting.id, user_id=participant_id, invitation_status=InvitationStatus.PENDING))
            NotificationService.create(
                participant_id,
                NotificationEvent.MEETING_INVITATION,
                "Invitación a reunión",
                f"Has sido invitado a: {meeting.title}",
                "Meeting",
                meeting.id,
            )

        AuditService.log(AuditEvent.MEETING_CREATED, creator.id, "Meeting", meeting.id, {"participant_ids": participant_ids})
        db.session.commit()
        return meeting, availability

    @staticmethod
    def list_for_user(user: User, filters: dict) -> list[Meeting]:
        MeetingService._ensure_can_operate_meetings(user, allow_secretary=True)
        query = Meeting.query
        if user.role.slug == RoleSlug.SECRETARY:
            pass
        else:
            created_ids = db.session.query(Meeting.id).filter(Meeting.created_by_user_id == user.id)
            invited_ids = db.session.query(MeetingParticipant.meeting_id).filter(MeetingParticipant.user_id == user.id)
            meeting_ids = {meeting_id for (meeting_id,) in created_ids.union(invited_ids).all()}
            if not meeting_ids:
                return []
            query = query.filter(Meeting.id.in_(meeting_ids))
        if filters.get("date_from"):
            query = query.filter(Meeting.date >= filters["date_from"])
        if filters.get("date_to"):
            query = query.filter(Meeting.date <= filters["date_to"])
        if filters.get("status"):
            query = query.filter(Meeting.status == filters["status"])
        if filters.get("created_by_me"):
            query = query.filter(Meeting.created_by_user_id == user.id)
        if filters.get("invited"):
            query = query.join(MeetingParticipant).filter(MeetingParticipant.user_id == user.id)
        if filters.get("pending_response"):
            query = query.join(MeetingParticipant).filter(
                MeetingParticipant.user_id == user.id,
                MeetingParticipant.invitation_status == InvitationStatus.PENDING,
            )
        return query.order_by(Meeting.date.asc(), Meeting.start_time.asc()).all()

    @staticmethod
    def get_detail(meeting_id: int, user: User) -> Meeting:
        meeting = db.session.get(Meeting, meeting_id)
        if not meeting:
            raise ValueError("Reunión no encontrada.")
        if not MeetingService.can_view(meeting, user):
            raise PermissionError("No tienes permisos para ver esta reunión.")
        return meeting

    @staticmethod
    def accept(meeting_id: int, user: User) -> MeetingParticipant:
        MeetingService._ensure_can_operate_meetings(user, allow_secretary=False)
        meeting, participant = MeetingService._get_participation(meeting_id, user.id)
        if meeting.status == MeetingStatus.CANCELLED:
            raise ValueError("La reunión está cancelada.")

        conflicts = AvailabilityService.user_blocking_conflicts(user.id, meeting.date, meeting.start_time, meeting.end_time, exclude_meeting_id=meeting.id)
        if conflicts:
            raise ValueError("No puedes aceptar: ya tienes una reunión confirmada en ese horario.")

        participant.invitation_status = InvitationStatus.ACCEPTED
        participant.responded_at = datetime.now(timezone.utc)
        participant.response_comment = None
        NotificationService.create(
            meeting.created_by_user_id,
            NotificationEvent.MEETING_ACCEPTED,
            "Invitación aceptada",
            f"{user.full_name} aceptó la reunión {meeting.title}",
            "Meeting",
            meeting.id,
        )
        AuditService.log(AuditEvent.MEETING_ACCEPTED, user.id, "Meeting", meeting.id)
        db.session.commit()
        return participant

    @staticmethod
    def reject(meeting_id: int, user: User, comment: str | None = None) -> MeetingParticipant:
        MeetingService._ensure_can_operate_meetings(user, allow_secretary=False)
        meeting, participant = MeetingService._get_participation(meeting_id, user.id)
        if meeting.status == MeetingStatus.CANCELLED:
            raise ValueError("La reunión está cancelada.")
        participant.invitation_status = InvitationStatus.REJECTED
        participant.responded_at = datetime.now(timezone.utc)
        participant.response_comment = comment
        NotificationService.create(
            meeting.created_by_user_id,
            NotificationEvent.MEETING_REJECTED,
            "Invitación rechazada",
            f"{user.full_name} rechazó la reunión {meeting.title}",
            "Meeting",
            meeting.id,
        )
        AuditService.log(AuditEvent.MEETING_REJECTED, user.id, "Meeting", meeting.id, {"comment": comment})
        db.session.commit()
        return participant

    @staticmethod
    def cancel(meeting_id: int, user: User, reason: str | None = None) -> Meeting:
        meeting = db.session.get(Meeting, meeting_id)
        if not meeting:
            raise ValueError("Reunión no encontrada.")
        if user.role.slug == RoleSlug.ADMIN:
            raise PermissionError("Admin no opera reuniones.")
        if meeting.created_by_user_id != user.id and user.role.slug != RoleSlug.SECRETARY:
            raise PermissionError("Solo el creador o Secretaría pueden cancelar.")
        if meeting.status == MeetingStatus.CANCELLED:
            raise ValueError("La reunión ya está cancelada.")

        meeting.status = MeetingStatus.CANCELLED
        meeting.cancelled_at = datetime.now(timezone.utc)
        meeting.cancellation_reason = reason
        for participant in meeting.participants:
            NotificationService.create(
                participant.user_id,
                NotificationEvent.MEETING_CANCELLED,
                "Reunión cancelada",
                f"Se canceló la reunión {meeting.title}",
                "Meeting",
                meeting.id,
            )
        AuditService.log(AuditEvent.MEETING_CANCELLED, user.id, "Meeting", meeting.id, {"reason": reason})
        db.session.commit()
        return meeting

    @staticmethod
    def can_view(meeting: Meeting, user: User) -> bool:
        if user.role.slug == RoleSlug.ADMIN:
            return False
        if user.role.slug == RoleSlug.SECRETARY:
            return True
        if meeting.created_by_user_id == user.id:
            return True
        return MeetingParticipant.query.filter_by(meeting_id=meeting.id, user_id=user.id).first() is not None

    @staticmethod
    def to_dict(meeting: Meeting) -> dict:
        return {
            "id": meeting.id,
            "title": meeting.title,
            "objective": meeting.objective,
            "agenda_items": meeting.agenda_items,
            "description": meeting.description,
            "date": meeting.date.isoformat(),
            "start_time": meeting.start_time.strftime("%H:%M"),
            "end_time": meeting.end_time.strftime("%H:%M"),
            "modality": meeting.modality,
            "status": meeting.status,
            "creator": {
                "id": meeting.creator.id,
                "full_name": meeting.creator.full_name,
                "email": meeting.creator.email,
            },
            "room": {"id": meeting.room.id, "name": meeting.room.name} if meeting.room else None,
            "participants": [
                {
                    "id": participant.user.id,
                    "full_name": participant.user.full_name,
                    "email": participant.user.email,
                    "invitation_status": participant.invitation_status,
                    "attendance_status": participant.attendance_status,
                    "response_comment": participant.response_comment,
                }
                for participant in meeting.participants
            ],
        }

    @staticmethod
    def _get_participation(meeting_id: int, user_id: int) -> tuple[Meeting, MeetingParticipant]:
        meeting = db.session.get(Meeting, meeting_id)
        if not meeting:
            raise ValueError("Reunión no encontrada.")
        participant = MeetingParticipant.query.filter_by(meeting_id=meeting_id, user_id=user_id).first()
        if not participant:
            raise PermissionError("No eres participante invitado.")
        return meeting, participant

    @staticmethod
    def _ensure_can_operate_meetings(user: User, allow_secretary: bool):
        if not user or not user.is_active:
            raise PermissionError("Usuario inactivo o no autenticado.")
        if user.role.slug == RoleSlug.ADMIN:
            raise PermissionError("Admin no opera reuniones.")
        if user.role.slug == RoleSlug.SECRETARY and not allow_secretary:
            raise PermissionError("Secretaría no puede realizar esta operación.")

    @staticmethod
    def _normalize_modality(modality: str) -> str:
        normalized = MeetingService.MODALITY_MAP.get(modality)
        if not normalized:
            raise ValueError("Modalidad inválida.")
        return normalized
