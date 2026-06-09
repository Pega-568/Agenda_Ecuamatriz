"""
app/attendance/models.py — Modelo: AttendanceToken (QR fijo)
Agenda Ecuamatriz
"""

from datetime import datetime, timezone
from app import db


class AttendanceToken(db.Model):
    """
    Token QR fijo por reunión.

    Primera versión: QR estático, no rotativo.
    El token se genera cuando se crea la reunión o a demanda del creador.
    La validez se calcula dinámicamente desde SystemSetting:
        - Válido desde: meeting.date + start_time - qr_valid_minutes_before
        - Válido hasta: meeting.date + end_time + qr_valid_minutes_after

    QR contiene: URL con token UUID para validación en el backend.
    El backend verifica todas las condiciones en el momento del escaneo.
    """

    __tablename__ = "attendance_tokens"

    id = db.Column(db.Integer, primary_key=True)

    meeting_id = db.Column(
        db.Integer,
        db.ForeignKey("meetings.id"),
        nullable=False,
        unique=True,         # Un solo QR por reunión
        index=True,
    )

    # Hash SHA-256 del token que va codificado en el QR.
    # El token plano solo se entrega al crear el QR y no se persiste.
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # ─── Relaciones ──────────────────────────────────────────────────────────
    meeting = db.relationship("Meeting", back_populates="attendance_token")
    created_by = db.relationship("User", foreign_keys=[created_by_user_id])

    def __repr__(self) -> str:
        return f"<AttendanceToken meeting={self.meeting_id} active={self.is_active}>"
