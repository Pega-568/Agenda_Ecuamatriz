"""Servicios de notificaciones internas."""

from app import db
from app.notifications.models import Notification


class NotificationEvent:
    MEETING_INVITATION = "meeting_invitation"
    MEETING_INVITED = "meeting_invited"
    MEETING_RESPONSE_REMINDER = "meeting_response_reminder"
    MEETING_STARTING_SOON = "meeting_starting_soon"
    MEETING_ACCEPTED = "meeting_accepted"
    MEETING_REJECTED = "meeting_rejected"
    MEETING_CANCELLED = "meeting_cancelled"
    MEETING_RESCHEDULED = "meeting_rescheduled"
    QR_AVAILABLE = "qr_available"
    ATTENDANCE_MARKED = "attendance_marked"
    MANUAL_ATTENDANCE_MARKED = "manual_attendance_marked"
    ATTENDANCE_ALREADY_MARKED = "attendance_already_marked"
    QR_INVALID = "qr_invalid"
    QR_NOT_ALLOWED = "qr_not_allowed"


class NotificationService:
    @staticmethod
    def create(user_id: int, event_type: str, title: str, message: str, entity_type: str | None = None, entity_id: int | None = None) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=event_type,
            title=title,
            message=message,
            related_entity_type=entity_type,
            related_entity_id=entity_id,
        )
        db.session.add(notification)
        return notification

    @staticmethod
    def list_for_user(user_id: int) -> list[Notification]:
        return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def get_dynamic_notifications(user) -> list[dict]:
        from app.meetings.models import MeetingParticipant, InvitationStatus, MeetingStatus, Meeting
        from datetime import datetime, timezone, timedelta
        
        dynamic_list = []
        now = datetime.now(timezone.utc)
        
        # 1. Reminders for pending invitations
        pending_participants = MeetingParticipant.query.filter_by(user_id=user.id, invitation_status=InvitationStatus.PENDING).all()
        for p in pending_participants:
            m = p.meeting
            if m.status != MeetingStatus.CANCELLED and datetime.combine(m.date, m.start_time).replace(tzinfo=timezone.utc) > now:
                dynamic_list.append({
                    "id": f"dyn_rem_{m.id}",
                    "type": NotificationEvent.MEETING_RESPONSE_REMINDER,
                    "title": "Recordatorio de Invitación",
                    "message": f"Tienes pendiente responder la invitación: {m.title}.",
                    "is_read": False,
                    "related_entity_type": "Meeting",
                    "related_entity_id": m.id,
                    "created_at": now.isoformat()
                })
        
        # 2. Starting soon (within 60 mins)
        # Accepted or Creator
        created_meetings = Meeting.query.filter_by(created_by_user_id=user.id, status=MeetingStatus.SCHEDULED).all()
        accepted_participants = MeetingParticipant.query.filter_by(user_id=user.id, invitation_status=InvitationStatus.ACCEPTED).all()
        upcoming_meetings = set(created_meetings + [p.meeting for p in accepted_participants if p.meeting.status == MeetingStatus.SCHEDULED])
        
        for m in upcoming_meetings:
            start_dt = datetime.combine(m.date, m.start_time).replace(tzinfo=timezone.utc)
            time_diff = start_dt - now
            if timedelta(minutes=0) <= time_diff <= timedelta(minutes=60):
                dynamic_list.append({
                    "id": f"dyn_soon_{m.id}",
                    "type": NotificationEvent.MEETING_STARTING_SOON,
                    "title": "Reunión Próxima",
                    "message": f"Tu reunión {m.title} inicia pronto.",
                    "is_read": False,
                    "related_entity_type": "Meeting",
                    "related_entity_id": m.id,
                    "created_at": now.isoformat()
                })
                
        return dynamic_list

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> Notification:
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if not notification:
            raise ValueError("Notificación no encontrada.")
        notification.mark_as_read()
        db.session.commit()
        return notification

    @staticmethod
    def to_dict(notification: Notification) -> dict:
        return {
            "id": notification.id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "related_entity_type": notification.related_entity_type,
            "related_entity_id": notification.related_entity_id,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
        }

    @staticmethod
    def notify_meeting_invited(user_id: int, title: str, meeting_id: int) -> Notification:
        return NotificationService.create(
            user_id=user_id,
            event_type=NotificationEvent.MEETING_INVITED,
            title="Nueva Invitación",
            message=f"Has sido invitado a la reunión: {title}.",
            entity_type="Meeting",
            entity_id=meeting_id
        )

    @staticmethod
    def notify_meeting_response_reminder(user_id: int, title: str, meeting_id: int) -> Notification:
        return NotificationService.create(
            user_id=user_id,
            event_type=NotificationEvent.MEETING_RESPONSE_REMINDER,
            title="Recordatorio de Invitación",
            message=f"Tienes pendiente responder la invitación: {title}.",
            entity_type="Meeting",
            entity_id=meeting_id
        )

    @staticmethod
    def notify_meeting_starting_soon(user_id: int, title: str, meeting_id: int) -> Notification:
        return NotificationService.create(
            user_id=user_id,
            event_type=NotificationEvent.MEETING_STARTING_SOON,
            title="Reunión Próxima",
            message=f"Tu reunión {title} inicia pronto.",
            entity_type="Meeting",
            entity_id=meeting_id
        )

    @staticmethod
    def notify_meeting_accepted(creator_id: int, participant_name: str, title: str, meeting_id: int) -> Notification:
        return NotificationService.create(
            user_id=creator_id,
            event_type=NotificationEvent.MEETING_ACCEPTED,
            title="Invitación Aceptada",
            message=f"{participant_name} aceptó la reunión: {title}.",
            entity_type="Meeting",
            entity_id=meeting_id
        )

    @staticmethod
    def notify_meeting_rejected(creator_id: int, participant_name: str, title: str, meeting_id: int) -> Notification:
        return NotificationService.create(
            user_id=creator_id,
            event_type=NotificationEvent.MEETING_REJECTED,
            title="Invitación Rechazada",
            message=f"{participant_name} rechazó la reunión: {title}.",
            entity_type="Meeting",
            entity_id=meeting_id
        )

    @staticmethod
    def notify_attendance_marked(user_id: int, title: str, meeting_id: int) -> Notification:
        return NotificationService.create(
            user_id=user_id,
            event_type=NotificationEvent.ATTENDANCE_MARKED,
            title="Asistencia Registrada",
            message=f"Asistencia registrada para la reunión: {title}.",
            entity_type="Meeting",
            entity_id=meeting_id
        )

    @staticmethod
    def notify_qr_error(user_id: int, error_type: str, message: str) -> Notification:
        notification = NotificationService.create(
            user_id=user_id,
            event_type=error_type,
            title="Error al escanear QR",
            message=message,
        )
        db.session.commit()
        return notification
