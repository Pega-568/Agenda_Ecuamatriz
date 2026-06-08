"""
app/audit/models.py — Modelo: AuditLog
Agenda Ecuamatriz
"""

from datetime import datetime, timezone
from app import db


class AuditLog(db.Model):
    """
    Registro de auditoría del sistema.

    Toda acción crítica debe registrar un AuditLog.
    Inmutable: no se actualizan ni eliminan registros de auditoría.

    Acciones auditables:
        meeting.create, meeting.update, meeting.cancel
        invitation.accept, invitation.reject
        attendance.mark_qr, attendance.mark_manual
        user.create, user.update, user.deactivate
        settings.update
        technical_sheet.create, technical_sheet.finalize
        report.export
        calendar.add_non_working_day, calendar.create_event
    """

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    # ─── Actor ───────────────────────────────────────────────────────────────
    actor_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    # Nullable: acciones del sistema (jobs, seeders) no tienen actor humano

    # ─── Acción ──────────────────────────────────────────────────────────────
    action = db.Column(db.String(100), nullable=False, index=True)
    # Formato: "entidad.verbo" — ej: "meeting.create", "user.deactivate"

    # ─── Entidad afectada ────────────────────────────────────────────────────
    entity_type = db.Column(db.String(50), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)

    # ─── Contexto adicional ──────────────────────────────────────────────────
    metadata_json = db.Column("metadata", db.JSON, nullable=True)
    # Puede incluir: valores anteriores, valores nuevos, IP, etc.

    # ─── Timestamp ───────────────────────────────────────────────────────────
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # ─── Relaciones ──────────────────────────────────────────────────────────
    actor = db.relationship("User", foreign_keys=[actor_user_id])

    def __repr__(self) -> str:
        return (
            f"<AuditLog id={self.id} action={self.action} "
            f"entity={self.entity_type}:{self.entity_id}>"
        )
