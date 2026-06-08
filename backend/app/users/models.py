"""
app/users/models.py — Modelo de datos: User
Agenda Ecuamatriz

Entidad central del sistema. Representa a cualquier colaborador interno.

Implementa flask_login.UserMixin para compatibilidad con Flask-Login
(autenticación web con sesiones servidor).
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """
    Colaborador interno de Ecuamatriz.

    Roles posibles (via FK a roles):
        - admin:     Administrador técnico. No participa en reuniones.
        - secretary: Secretaría institucional.
        - user:      Colaborador que crea y participa en reuniones.

    Flask-Login (UserMixin) provee:
        - is_authenticated: True si el usuario está logueado
        - is_active:        Delegado a la propiedad is_active de la columna
        - is_anonymous:     Siempre False para usuarios reales
        - get_id():         Retorna str(self.id) para la sesión

    NOTA: is_active existe como columna en la BD (override de UserMixin).
    Flask-Login respetará el valor de la columna al verificar si el usuario
    puede iniciar sesión.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # ─── Datos personales ────────────────────────────────────────────────────
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True)
    position = db.Column(db.String(150), nullable=True)  # Cargo en la empresa

    # ─── Autenticación ───────────────────────────────────────────────────────
    password_hash = db.Column(db.String(255), nullable=False)

    # ─── Rol y área ──────────────────────────────────────────────────────────
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=True)

    # ─── Notificaciones push (Android, Fase 7) ───────────────────────────────
    # Token FCM actualizado cuando el usuario inicia sesión en la app Android.
    fcm_token = db.Column(db.String(512), nullable=True)

    # ─── Estado ──────────────────────────────────────────────────────────────
    # IMPORTANTE: Esta columna hace override a UserMixin.is_active.
    # Flask-Login verifica is_active antes de permitir login.
    # Un usuario desactivado (is_active=False) no puede iniciar sesión.
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # ─── Timestamps ──────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login_at = db.Column(db.DateTime, nullable=True)

    # ─── Relaciones ──────────────────────────────────────────────────────────
    role = db.relationship("Role", back_populates="users", lazy="joined")
    area = db.relationship("Area", back_populates="users", lazy="joined")
    created_meetings = db.relationship(
        "Meeting",
        foreign_keys="Meeting.created_by_user_id",
        back_populates="creator",
        lazy="dynamic",
    )
    participations = db.relationship(
        "MeetingParticipant",
        foreign_keys="MeetingParticipant.user_id",
        back_populates="user",
        lazy="dynamic",
    )
    notifications = db.relationship(
        "Notification",
        foreign_keys="Notification.user_id",
        back_populates="user",
        lazy="dynamic",
    )

    # ─── Flask-Login: get_id() ────────────────────────────────────────────────
    def get_id(self) -> str:
        """
        Requerido por Flask-Login.
        Retorna el ID del usuario como string para almacenar en la sesión.
        El load_user en app/__init__.py lo convierte de vuelta a int para la BD.
        """
        return str(self.id)

    # ─── Propiedades calculadas ───────────────────────────────────────────────
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def role_slug(self) -> str:
        """Atajo para obtener el slug del rol sin cargar relación."""
        return self.role.slug if self.role else ""

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role_id}>"
