"""Servicio de QR fijo y control de asistencia."""

from datetime import datetime, timezone
import hashlib
import secrets

from flask import current_app

from app import db
from app.attendance.models import AttendanceToken
from app.audit.service import AuditEvent, AuditService
from app.meetings.models import AttendanceMethod, AttendanceStatus, InvitationStatus, Meeting, MeetingParticipant, MeetingStatus
from app.notifications.service import NotificationEvent, NotificationService
from app.roles.models import RoleSlug
from app.settings.service import SettingsService
from app.users.models import User


class AttendanceService:
    @staticmethod
    def generate_or_get_attendance_token(meeting_id: int, actor_user: User) -> dict:
        meeting = AttendanceService._meeting_or_error(meeting_id)
        AttendanceService._ensure_can_manage_attendance(meeting, actor_user)
        if meeting.status == MeetingStatus.CANCELLED:
            raise ValueError("La reunión está cancelada.")

        # Invalidar tokens anteriores activos (reutilizando el registro por restricción UNIQUE)
        existing_token = AttendanceToken.query.filter_by(meeting_id=meeting.id).first()
        plain_token = secrets.token_urlsafe(32)
        new_hash = AttendanceService._hash_token(plain_token)

        if existing_token:
            existing_token.token_hash = new_hash
            existing_token.is_active = True
            existing_token.created_by_user_id = actor_user.id
            token = existing_token
        else:
            token = AttendanceToken(
                meeting_id=meeting.id,
                token_hash=new_hash,
                is_active=True,
                created_by_user_id=actor_user.id,
            )
            db.session.add(token)
            
        db.session.flush()
        AuditService.log(AuditEvent.ATTENDANCE_TOKEN_CREATED, actor_user.id, "AttendanceToken", token.id, {"meeting_id": meeting.id})
        NotificationService.create(
            meeting.created_by_user_id,
            NotificationEvent.QR_AVAILABLE,
            "QR de asistencia disponible",
            f"El QR de asistencia está disponible para: {meeting.title}",
            "Meeting",
            meeting.id,
        )
        db.session.commit()

        valid_from, valid_until = AttendanceService.valid_window(meeting)
        attendance_url = AttendanceService._attendance_url(plain_token)
        return {
            "meeting_id": meeting.id,
            "attendance_url": attendance_url,
            "qr_payload": attendance_url,
            "token_available": True,
            "token_created": True,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
        }

    @staticmethod
    def mark_by_qr(plain_token: str, actor_user: User) -> MeetingParticipant:
        if not actor_user or not actor_user.is_active:
            raise PermissionError("Usuario no autenticado o inactivo.")
        settings = AttendanceService._settings()
        if not settings["qr_attendance_enabled"]:
            raise ValueError("La asistencia por QR está deshabilitada.")
        if settings["require_login_for_qr_attendance"] and not actor_user:
            raise PermissionError("Login requerido para marcar asistencia.")

        token = AttendanceToken.query.filter_by(token_hash=AttendanceService._hash_token(plain_token), is_active=True).first()
        if not token:
            NotificationService.notify_qr_error(actor_user.id, NotificationEvent.QR_INVALID, "Token QR inválido.")
            raise ValueError("Token QR inválido.")
        meeting = token.meeting
        if meeting.status == MeetingStatus.CANCELLED:
            raise ValueError("La reunión está cancelada.")
        AttendanceService._ensure_now_in_window(meeting)

        participant = MeetingParticipant.query.filter_by(meeting_id=meeting.id, user_id=actor_user.id).first()
        if not participant:
            NotificationService.notify_qr_error(actor_user.id, NotificationEvent.QR_NOT_ALLOWED, "El usuario no es participante de esta reunión.")
            raise PermissionError("El usuario no es participante de esta reunión.")
        if participant.invitation_status != InvitationStatus.ACCEPTED:
            NotificationService.notify_qr_error(actor_user.id, NotificationEvent.QR_NOT_ALLOWED, "Solo participantes con invitación aceptada pueden marcar asistencia por QR.")
            raise ValueError("Solo participantes con invitación aceptada pueden marcar asistencia por QR.")
        if participant.attendance_status != AttendanceStatus.NOT_MARKED:
            NotificationService.notify_qr_error(actor_user.id, NotificationEvent.ATTENDANCE_ALREADY_MARKED, "Tu asistencia ya fue registrada.")
            raise ValueError("Asistencia ya registrada.")

        participant.attendance_status = AttendanceStatus.PRESENT
        participant.attendance_method = AttendanceMethod.QR
        participant.attendance_marked_at = datetime.now(timezone.utc)
        participant.attendance_marked_by_user_id = actor_user.id
        participant.attendance_comment = None
        AuditService.log(AuditEvent.ATTENDANCE_MARKED_QR, actor_user.id, "Meeting", meeting.id, {"participant_id": participant.id})
        NotificationService.notify_attendance_marked(
            user_id=actor_user.id,
            title=meeting.title,
            meeting_id=meeting.id
        )
        db.session.commit()
        return participant

    @staticmethod
    def attendance_report(meeting_id: int, actor_user: User) -> dict:
        meeting = AttendanceService._meeting_or_error(meeting_id)
        AttendanceService._ensure_can_manage_attendance(meeting, actor_user)
        participants = meeting.participants.order_by(MeetingParticipant.user_id.asc()).all()
        summary = {
            "total_invited": len(participants),
            AttendanceStatus.PRESENT: 0,
            AttendanceStatus.ABSENT: 0,
            AttendanceStatus.NOT_MARKED: 0,
            AttendanceStatus.JUSTIFIED: 0,
        }
        items = []
        for participant in participants:
            summary[participant.attendance_status] = summary.get(participant.attendance_status, 0) + 1
            items.append(AttendanceService.participant_to_dict(participant))
        return {"meeting_id": meeting.id, "summary": summary, "participants": items}

    @staticmethod
    def mark_manual(meeting_id: int, actor_user: User, user_id: int, attendance_status: str, comment: str | None = None) -> MeetingParticipant:
        meeting = AttendanceService._meeting_or_error(meeting_id)
        if meeting.status == MeetingStatus.CANCELLED:
            raise ValueError("La reunión está cancelada.")
        if actor_user.role.slug == RoleSlug.ADMIN:
            raise PermissionError("Admin no opera asistencia.")

        settings = AttendanceService._settings()
        is_secretary = actor_user.role.slug == RoleSlug.SECRETARY
        is_creator = meeting.created_by_user_id == actor_user.id
        if is_secretary:
            if not settings["allow_manual_attendance_by_secretary"]:
                raise PermissionError("Marcado manual por Secretaría deshabilitado.")
            method = AttendanceMethod.MANUAL_SECRETARY
        elif is_creator:
            if not settings["allow_manual_attendance_by_creator"]:
                raise PermissionError("Marcado manual por creador deshabilitado.")
            method = AttendanceMethod.MANUAL_CREATOR
        else:
            raise PermissionError("No tienes permisos para marcar asistencia manual.")

        participant = MeetingParticipant.query.filter_by(meeting_id=meeting.id, user_id=user_id).first()
        if not participant:
            raise ValueError("Participante no encontrado.")
        if participant.invitation_status == InvitationStatus.REJECTED and not is_secretary:
            raise PermissionError("Solo Secretaría puede marcar asistencia de usuarios que rechazaron.")
        if participant.invitation_status == InvitationStatus.REJECTED and is_secretary and not comment:
            raise ValueError("Comentario obligatorio para marcar manualmente a un usuario que rechazó.")

        participant.attendance_status = attendance_status
        participant.attendance_method = method
        participant.attendance_marked_at = datetime.now(timezone.utc)
        participant.attendance_marked_by_user_id = actor_user.id
        participant.attendance_comment = comment
        if attendance_status == AttendanceStatus.JUSTIFIED:
            participant.attendance_justification = comment
        AuditService.log(
            AuditEvent.ATTENDANCE_MARKED_MANUAL,
            actor_user.id,
            "Meeting",
            meeting.id,
            {"participant_id": participant.id, "attendance_status": attendance_status, "method": method},
        )
        NotificationService.create(
            participant.user_id,
            NotificationEvent.MANUAL_ATTENDANCE_MARKED,
            "Asistencia actualizada",
            f"Tu asistencia fue actualizada en {meeting.title}",
            "Meeting",
            meeting.id,
        )
        db.session.commit()
        return participant

    @staticmethod
    def participant_to_dict(participant: MeetingParticipant) -> dict:
        return {
            "user_id": participant.user_id,
            "full_name": participant.user.full_name,
            "invitation_status": participant.invitation_status,
            "attendance_status": participant.attendance_status,
            "attendance_method": participant.attendance_method,
            "attendance_marked_at": participant.attendance_marked_at.isoformat() if participant.attendance_marked_at else None,
            "attendance_marked_by_user_id": participant.attendance_marked_by_user_id,
            "attendance_comment": participant.attendance_comment,
        }

    @staticmethod
    def valid_window(meeting: Meeting) -> tuple[datetime, datetime]:
        settings = AttendanceService._settings()
        start = datetime.combine(meeting.date, meeting.start_time)
        end = datetime.combine(meeting.date, meeting.end_time)
        before = settings["qr_valid_before_minutes"]
        after = settings["qr_valid_after_minutes"]
        from datetime import timedelta

        return start - timedelta(minutes=before), end + timedelta(minutes=after)

    @staticmethod
    def _ensure_now_in_window(meeting: Meeting):
        valid_from, valid_until = AttendanceService.valid_window(meeting)
        now = AttendanceService._now_for_window()
        if now < valid_from:
            raise ValueError("QR aún no válido.")
        if now > valid_until:
            raise ValueError("QR expirado.")

    @staticmethod
    def _now_for_window() -> datetime:
        return datetime.now()

    @staticmethod
    def _settings() -> dict:
        SettingsService.seed_defaults()
        settings = {setting.key: setting.get_typed_value() for setting in SettingsService.list_settings()}
        return {
            "qr_attendance_enabled": settings.get("qr_attendance_enabled", True),
            "qr_valid_before_minutes": settings.get("qr_valid_before_minutes", 10),
            "qr_valid_after_minutes": settings.get("qr_valid_after_minutes", 20),
            "allow_manual_attendance_by_secretary": settings.get("allow_manual_attendance_by_secretary", True),
            "allow_manual_attendance_by_creator": settings.get("allow_manual_attendance_by_creator", False),
            "require_login_for_qr_attendance": settings.get("require_login_for_qr_attendance", True),
        }

    @staticmethod
    def _meeting_or_error(meeting_id: int) -> Meeting:
        meeting = db.session.get(Meeting, meeting_id)
        if not meeting:
            raise ValueError("Reunión no encontrada.")
        return meeting

    @staticmethod
    def _ensure_can_manage_attendance(meeting: Meeting, actor_user: User):
        if not actor_user or not actor_user.is_active:
            raise PermissionError("Usuario inactivo o no autenticado.")
        if actor_user.role.slug == RoleSlug.ADMIN:
            raise PermissionError("Admin no opera asistencia.")
        if actor_user.role.slug == RoleSlug.SECRETARY:
            return
        if meeting.created_by_user_id == actor_user.id:
            return
        raise PermissionError("Solo el creador o Secretaría pueden operar asistencia.")

    @staticmethod
    def _hash_token(plain_token: str) -> str:
        return hashlib.sha256(plain_token.encode("utf-8")).hexdigest()

    @staticmethod
    def _attendance_url(plain_token: str) -> str:
        base_url = current_app.config.get("APP_URL", "http://127.0.0.1:5000").rstrip("/")
        return f"{base_url}/attendance/qr/{plain_token}"
