"""
app/technical_sheets/models.py — Modelo: TechnicalSheet
Agenda Ecuamatriz
"""

from datetime import datetime, timezone
from app import db


class TechnicalSheetStatus:
    """Estados de la ficha técnica."""
    DRAFT = "draft"             # En edición
    FINALIZED = "finalized"     # Cerrada y finalizada

    ALL = [DRAFT, FINALIZED]


class TechnicalSheet(db.Model):
    """
    Ficha técnica / acta de reunión.

    Primera versión: manual/asistida.
    Los datos base se autocompletan desde la reunión.
    El creador/coordinador edita los campos de contenido.

    Versión futura (Fase 8): borrador desde transcripción de audio.
    """

    __tablename__ = "technical_sheets"

    id = db.Column(db.Integer, primary_key=True)

    meeting_id = db.Column(
        db.Integer,
        db.ForeignKey("meetings.id"),
        nullable=False,
        unique=True,    # Una sola ficha por reunión
        index=True,
    )

    # ─── Campos editables por el creador/coordinador ─────────────────────
    topics_discussed = db.Column(db.Text, nullable=True)
    executive_summary = db.Column(db.Text, nullable=True)
    agreements = db.Column(db.Text, nullable=True)
    commitments = db.Column(db.Text, nullable=True)
    observations = db.Column(db.Text, nullable=True)

    # ─── Estado ──────────────────────────────────────────────────────────
    status = db.Column(
        db.String(20),
        nullable=False,
        default=TechnicalSheetStatus.DRAFT,
    )

    # ─── Auditoría ───────────────────────────────────────────────────────
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    finalized_at = db.Column(db.DateTime, nullable=True)

    # ─── Futuro (Fase 8) — integración con transcripción ─────────────────
    # generated_from_transcript: bool — Si fue generada desde transcripción
    # transcript_id: FK a MeetingTranscript
    # (Campos comentados hasta Fase 8, no crear columnas todavía)

    # ─── Relaciones ──────────────────────────────────────────────────────
    meeting = db.relationship("Meeting", back_populates="technical_sheet")
    created_by = db.relationship("User", foreign_keys=[created_by_user_id])

    def finalize(self):
        """Marca la ficha como finalizada."""
        self.status = TechnicalSheetStatus.FINALIZED
        self.finalized_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<TechnicalSheet id={self.id} meeting={self.meeting_id} status={self.status}>"
