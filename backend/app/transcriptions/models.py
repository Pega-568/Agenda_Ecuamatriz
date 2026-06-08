"""
app/transcriptions/models.py — Modelos: MeetingTranscript, TechnicalSheetDraft (FUTURO — Fase 8)
Agenda Ecuamatriz

⚠️  No instanciar ni migrar hasta Fase 8.
"""

from datetime import datetime, timezone
from app import db


class MeetingTranscript(db.Model):
    """
    Transcripción de texto generada desde grabación.

    FUTURO (Fase 8).
    REGLA: La transcripción genera BORRADOR, no ficha técnica final.
    Siempre requiere revisión humana.
    """

    __tablename__ = "meeting_transcripts"

    id = db.Column(db.Integer, primary_key=True)
    recording_id = db.Column(
        db.Integer, db.ForeignKey("meeting_recordings.id"), nullable=False
    )
    meeting_id = db.Column(
        db.Integer, db.ForeignKey("meetings.id"), nullable=False, index=True
    )

    transcript_text = db.Column(db.Text, nullable=True)
    provider = db.Column(db.String(50), nullable=True)
    # Ej: "openai_whisper", "google_speech", "pending"

    status = db.Column(db.String(30), nullable=False, default="pending")
    # pending | processing | completed | failed

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<MeetingTranscript id={self.id} meeting={self.meeting_id} status={self.status}>"


class TechnicalSheetDraft(db.Model):
    """
    Borrador de ficha técnica generado desde transcripción.

    FUTURO (Fase 8).
    Este borrador requiere revisión y aprobación humana
    antes de convertirse en TechnicalSheet finalizada.
    """

    __tablename__ = "technical_sheet_drafts"

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(
        db.Integer, db.ForeignKey("meetings.id"), nullable=False, index=True
    )
    transcript_id = db.Column(
        db.Integer, db.ForeignKey("meeting_transcripts.id"), nullable=True
    )

    # Borrador generado por IA — no usar como final sin revisión
    draft_topics = db.Column(db.Text, nullable=True)
    draft_summary = db.Column(db.Text, nullable=True)
    draft_agreements = db.Column(db.Text, nullable=True)

    reviewed_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    reviewed_at = db.Column(db.DateTime, nullable=True)
    is_approved = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<TechnicalSheetDraft id={self.id} meeting={self.meeting_id} approved={self.is_approved}>"
