"""
app/calendar/models.py — Modelos: WorkCalendarDay, InstitutionalEvent
Agenda Ecuamatriz
"""

from datetime import datetime, timezone
from app import db


class WorkSchedule(db.Model):
    """
    Horario laboral por día de semana.

    weekday usa ISO: 1=lunes ... 7=domingo.
    """

    __tablename__ = "work_schedules"

    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.Integer, unique=True, nullable=False, index=True)
    is_working_day = db.Column(db.Boolean, default=True, nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<WorkSchedule weekday={self.weekday} working={self.is_working_day}>"


class WorkCalendarDay(db.Model):
    """
    Día del calendario laboral.

    Registra días no laborables, feriados y excepciones.
    Si un día no está en esta tabla, se considera laborable por defecto
    (según la configuración de working_days en SystemSetting).
    """

    __tablename__ = "work_calendar_days"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False, index=True)
    is_working_day = db.Column(db.Boolean, nullable=False)
    blocks_meetings = db.Column(db.Boolean, default=True, nullable=False)
    # Si blocks_meetings=True: bloqueo duro (no se puede crear reunión)
    # Si blocks_meetings=False: solo advertencia

    label = db.Column(db.String(150), nullable=True)   # Ej: "Feriado Nacional"
    reason = db.Column(db.Text, nullable=True)

    # ─── Auditoría ───────────────────────────────────────────────────────────
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<WorkCalendarDay date={self.date} working={self.is_working_day}>"


class InstitutionalEvent(db.Model):
    """
    Evento institucional de Ecuamatriz.
    Gestionado por Secretaría.

    Si blocks_agenda=True: bloquea la creación de reuniones en esa franja.
    """

    __tablename__ = "institutional_events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)

    blocks_agenda = db.Column(db.Boolean, default=False, nullable=False)
    # Si True: nadie puede crear reunión en ese horario.

    # ─── Auditoría ───────────────────────────────────────────────────────────
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

    def __repr__(self) -> str:
        return f"<InstitutionalEvent id={self.id} title={self.title} date={self.date}>"
