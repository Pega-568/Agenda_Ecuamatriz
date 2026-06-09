"""Servicios de auditoría."""

from app import db
from app.audit.models import AuditLog


class AuditEvent:
    MEETING_CREATED = "meeting_created"
    MEETING_ACCEPTED = "meeting_accepted"
    MEETING_REJECTED = "meeting_rejected"
    MEETING_CANCELLED = "meeting_cancelled"
    ATTENDANCE_TOKEN_CREATED = "attendance_token_created"
    ATTENDANCE_MARKED_QR = "attendance_marked_qr"
    ATTENDANCE_MARKED_MANUAL = "attendance_marked_manual"


class AuditService:
    @staticmethod
    def log(action: str, actor_user_id: int | None = None, entity_type: str | None = None, entity_id: int | None = None, metadata: dict | None = None) -> AuditLog:
        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata,
        )
        db.session.add(entry)
        return entry
