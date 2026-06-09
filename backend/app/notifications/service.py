"""Servicios de notificaciones internas."""

from app import db
from app.notifications.models import Notification


class NotificationEvent:
    MEETING_INVITATION = "meeting_invitation"
    MEETING_ACCEPTED = "meeting_accepted"
    MEETING_REJECTED = "meeting_rejected"
    MEETING_CANCELLED = "meeting_cancelled"
    QR_AVAILABLE = "qr_available"
    ATTENDANCE_MARKED = "attendance_marked"
    MANUAL_ATTENDANCE_MARKED = "manual_attendance_marked"


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
