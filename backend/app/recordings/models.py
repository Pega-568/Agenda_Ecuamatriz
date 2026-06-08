"""
app/recordings/models.py — Modelo: MeetingRecording (FUTURO — Fase 8)
Agenda Ecuamatriz

⚠️  No instanciar ni migrar hasta Fase 8.
    Modelo preparado para integración futura de grabación/transcripción.
"""

from datetime import datetime
from app import db


class MeetingRecording(db.Model):
    """
    Grabación de audio/video de una reunión.

    FUTURO (Fase 8): No implementar hasta recibir código del módulo externo.

    Campos preparados para:
    - Almacenamiento local o en nube (S3, GCS).
    - Integración con TranscriptionProvider.
    """

    __tablename__ = "meeting_recordings"

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(
        db.Integer, db.ForeignKey("meetings.id"), nullable=False, index=True
    )

    file_path = db.Column(db.String(512), nullable=True)
    storage_provider = db.Column(db.String(50), nullable=True)
    # Ej: "local", "s3", "gcs"

    duration_seconds = db.Column(db.Integer, nullable=True)
    file_size_bytes = db.Column(db.BigInteger, nullable=True)
    mime_type = db.Column(db.String(50), nullable=True)

    status = db.Column(db.String(30), nullable=False, default="pending")
    # Estados: pending | processing | ready | failed

    started_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<MeetingRecording id={self.id} meeting={self.meeting_id} status={self.status}>"
