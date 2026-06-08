"""
app/settings/models.py — Modelo de datos: SystemSetting
Agenda Ecuamatriz

Patrón: tabla key-value para configuración del sistema.
Permite al Administrador configurar parámetros sin tocar código.
"""

from datetime import datetime, timezone
from app import db


class SystemSetting(db.Model):
    """
    Parámetro de configuración del sistema.

    Parámetros esperados (keys):
        max_participants_per_meeting    int     Máximo de participantes por reunión
        max_meeting_duration_minutes    int     Duración máxima de reunión en minutos
        min_advance_hours               int     Horas mínimas de anticipación para crear reunión
        work_start_time                 str     Hora inicio jornada laboral (HH:MM)
        work_end_time                   str     Hora fin jornada laboral (HH:MM)
        working_days                    str     Días laborables separados por coma (1=lun, 7=dom)
        allow_meetings_outside_hours    bool    Permitir reuniones fuera de horario laboral
        allow_meetings_on_non_working   bool    Permitir reuniones en días no laborables
        qr_valid_minutes_before         int     Minutos antes del inicio que el QR es válido
        qr_valid_minutes_after          int     Minutos después del fin que el QR es válido
        notifications_reminder_minutes  int     Minutos antes de la reunión para recordatorio
        allow_manual_attendance_secretary bool  Secretaría puede marcar asistencia manual
        allow_manual_attendance_creator bool   Creador puede marcar asistencia manual
    """

    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    data_type = db.Column(
        db.String(20),
        nullable=False,
        default="string",
    )
    # Tipos válidos: string | int | bool | json
    description = db.Column(db.Text, nullable=True)

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    def get_typed_value(self):
        """Retorna el valor convertido al tipo correcto."""
        if self.data_type == "int":
            return int(self.value)
        if self.data_type == "bool":
            return self.value.lower() in ("true", "1", "yes")
        if self.data_type == "json":
            import json
            return json.loads(self.value)
        return self.value  # string

    def __repr__(self) -> str:
        return f"<SystemSetting key={self.key} value={self.value}>"
