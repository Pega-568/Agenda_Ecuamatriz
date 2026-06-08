"""
app/meetings/models.py — Modelos: Meeting, MeetingParticipant
Agenda Ecuamatriz

FLUJO ÚNICO DE REUNIÓN:
    Nueva reunión → datos generales → orden del día → fecha/hora/sala
    → participantes → disponibilidad → confirmación → invitación
    → aceptación/rechazo → asistencia QR → ficha técnica posterior
"""

from datetime import datetime
from app import db


class MeetingStatus:
    """Estados posibles de una reunión."""
    SCHEDULED = "scheduled"       # Creada y activa
    CANCELLED = "cancelled"       # Cancelada por el creador
    COMPLETED = "completed"       # Reunión ya ocurrió (fin de jornada)
    RESCHEDULED = "rescheduled"   # Reprogramada (genera nueva reunión)

    ALL = [SCHEDULED, CANCELLED, COMPLETED, RESCHEDULED]


class MeetingModality:
    """Modalidad de la reunión."""
    IN_PERSON = "in_person"       # Presencial (requiere sala)
    VIRTUAL = "virtual"           # Virtual (requiere virtual_link)
    HYBRID = "hybrid"             # Híbrida (sala + link)

    ALL = [IN_PERSON, VIRTUAL, HYBRID]


class InvitationStatus:
    """Estado de la invitación de un participante."""
    PENDING = "pending"           # No ha respondido
    ACCEPTED = "accepted"         # Aceptó la reunión
    REJECTED = "rejected"         # Rechazó la reunión

    ALL = [PENDING, ACCEPTED, REJECTED]


class AttendanceStatus:
    """Estado de asistencia real (independiente de invitación)."""
    NOT_MARKED = "not_marked"     # Sin marcar
    PRESENT = "present"           # Presente (asistió)
    ABSENT = "absent"             # Ausente
    JUSTIFIED = "justified"       # Ausencia justificada

    ALL = [NOT_MARKED, PRESENT, ABSENT, JUSTIFIED]


class AttendanceMethod:
    """Método por el que se marcó la asistencia."""
    QR = "qr"                              # Escaneó QR
    MANUAL_SECRETARY = "manual_secretary"  # Marcado por Secretaría
    MANUAL_CREATOR = "manual_creator"      # Marcado por el creador de la reunión

    ALL = [QR, MANUAL_SECRETARY, MANUAL_CREATOR]


class Meeting(db.Model):
    """
    Reunión empresarial.

    Campos obligatorios para crear reunión:
        - title, objective, agenda_items, date,
          start_time, end_time, modality, created_by_user_id
        - room_id si modality = in_person o hybrid
        - virtual_link si modality = virtual o hybrid
        - Al menos un participante
    """

    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)

    # ─── Datos generales ────────────────────────────────────────────────────
    title = db.Column(db.String(255), nullable=False)
    objective = db.Column(db.Text, nullable=False)
    agenda_items = db.Column(db.JSON, nullable=False)
    # agenda_items: lista de strings/objetos con los puntos del orden del día
    # Ej: ["Revisión de presupuesto", "Planificación Q3", "Puntos varios"]
    description = db.Column(db.Text, nullable=True)

    # ─── Fecha y hora ────────────────────────────────────────────────────────
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # ─── Lugar ───────────────────────────────────────────────────────────────
    modality = db.Column(
        db.String(20),
        nullable=False,
        default=MeetingModality.IN_PERSON,
    )
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=True)
    virtual_link = db.Column(db.String(512), nullable=True)

    # ─── Creador ─────────────────────────────────────────────────────────────
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )

    # ─── Estado ──────────────────────────────────────────────────────────────
    status = db.Column(
        db.String(20),
        nullable=False,
        default=MeetingStatus.SCHEDULED,
        index=True,
    )

    # ─── Timestamps ──────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancellation_reason = db.Column(db.Text, nullable=True)

    # ─── Relaciones ──────────────────────────────────────────────────────────
    creator = db.relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="created_meetings",
        lazy="joined",
    )
    room = db.relationship("Room", back_populates="meetings", lazy="joined")
    participants = db.relationship(
        "MeetingParticipant",
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    technical_sheet = db.relationship(
        "TechnicalSheet",
        back_populates="meeting",
        uselist=False,
        lazy="joined",
    )
    attendance_token = db.relationship(
        "AttendanceToken",
        back_populates="meeting",
        uselist=False,
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<Meeting id={self.id} title={self.title!r} date={self.date} status={self.status}>"


class MeetingParticipant(db.Model):
    """
    Participante de una reunión.

    Separa invitación de asistencia real:
        - invitation_status: ¿Aceptó/rechazó la invitación?
        - attendance_status: ¿Asistió físicamente a la reunión?

    REGLA: La reunión bloquea la agenda del CREADOR automáticamente.
    Para los invitados, solo bloquea si invitation_status = accepted.
    """

    __tablename__ = "meeting_participants"

    id = db.Column(db.Integer, primary_key=True)

    meeting_id = db.Column(
        db.Integer, db.ForeignKey("meetings.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    # ─── Estado de invitación ─────────────────────────────────────────────
    invitation_status = db.Column(
        db.String(20),
        nullable=False,
        default=InvitationStatus.PENDING,
    )
    response_comment = db.Column(db.Text, nullable=True)   # Comentario al rechazar
    responded_at = db.Column(db.DateTime, nullable=True)

    # ─── Estado de asistencia ─────────────────────────────────────────────
    attendance_status = db.Column(
        db.String(20),
        nullable=False,
        default=AttendanceStatus.NOT_MARKED,
    )
    attendance_method = db.Column(db.String(30), nullable=True)
    attendance_marked_at = db.Column(db.DateTime, nullable=True)
    attendance_justification = db.Column(db.Text, nullable=True)

    # ─── Constraints ─────────────────────────────────────────────────────
    __table_args__ = (
        db.UniqueConstraint("meeting_id", "user_id", name="uq_meeting_participant"),
    )

    # ─── Relaciones ──────────────────────────────────────────────────────
    meeting = db.relationship("Meeting", back_populates="participants")
    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="participations",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return (
            f"<MeetingParticipant meeting={self.meeting_id} "
            f"user={self.user_id} inv={self.invitation_status} "
            f"att={self.attendance_status}>"
        )
