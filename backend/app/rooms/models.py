"""
app/rooms/models.py — Modelo de datos: Room
Agenda Ecuamatriz
"""

from datetime import datetime, timezone
from app import db


class Room(db.Model):
    """
    Sala de reunión física.
    La modalidad virtual no requiere sala física.
    """

    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    location = db.Column(db.String(255), nullable=True)   # Piso, edificio, etc.
    capacity = db.Column(db.Integer, nullable=False)       # Máximo de personas
    description = db.Column(db.Text, nullable=True)
    has_projector = db.Column(db.Boolean, default=False)
    has_video_conference = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # ─── Timestamps ──────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ─── Relaciones ──────────────────────────────────────────────────────────
    meetings = db.relationship("Meeting", back_populates="room", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Room id={self.id} name={self.name} capacity={self.capacity}>"
