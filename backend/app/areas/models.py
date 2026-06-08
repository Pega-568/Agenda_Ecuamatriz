"""
app/areas/models.py — Modelo de datos: Area
Agenda Ecuamatriz
"""

from datetime import datetime, timezone
from app import db


class Area(db.Model):
    """
    Área organizacional de Ecuamatriz.
    Los usuarios pertenecen a un área.
    """

    __tablename__ = "areas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
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
    users = db.relationship("User", back_populates="area", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Area id={self.id} name={self.name}>"
