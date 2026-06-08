"""
app/notifications/models.py — Modelo: Notification
Agenda Ecuamatriz
"""

from datetime import datetime, timezone
from app import db


class NotificationType:
    """Tipos de notificación del sistema."""
    INVITATION_RECEIVED = "invitation_received"
    INVITATION_ACCEPTED = "invitation_accepted"
    INVITATION_REJECTED = "invitation_rejected"
    MEETING_CANCELLED = "meeting_cancelled"
    MEETING_RESCHEDULED = "meeting_rescheduled"
    MEETING_REMINDER = "meeting_reminder"
    QR_AVAILABLE = "qr_available"
    TECHNICAL_SHEET_PENDING = "technical_sheet_pending"
    INSTITUTIONAL_EVENT_CREATED = "institutional_event_created"
    NON_WORKING_DAY_ADDED = "non_working_day_added"

    ALL = [
        INVITATION_RECEIVED,
        INVITATION_ACCEPTED,
        INVITATION_REJECTED,
        MEETING_CANCELLED,
        MEETING_RESCHEDULED,
        MEETING_REMINDER,
        QR_AVAILABLE,
        TECHNICAL_SHEET_PENDING,
        INSTITUTIONAL_EVENT_CREATED,
        NON_WORKING_DAY_ADDED,
    ]


class Notification(db.Model):
    """
    Notificación interna del sistema para un usuario.

    Canal web: campana superior + centro de notificaciones.
    Canal Android: Firebase Cloud Messaging (Fase 7).
    """

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    # ─── Destinatario ────────────────────────────────────────────────────────
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    # ─── Contenido ───────────────────────────────────────────────────────────
    type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

    # ─── Referencia a entidad relacionada ────────────────────────────────────
    related_entity_type = db.Column(db.String(50), nullable=True)
    # Ej: "Meeting", "InstitutionalEvent"
    related_entity_id = db.Column(db.Integer, nullable=True)

    # ─── Estado ──────────────────────────────────────────────────────────────
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)

    # ─── Timestamps ──────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)

    # ─── Relaciones ──────────────────────────────────────────────────────────
    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="notifications",
        lazy="joined",
    )

    def mark_as_read(self):
        """Marca la notificación como leída."""
        self.is_read = True
        self.read_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user={self.user_id} type={self.type} read={self.is_read}>"
