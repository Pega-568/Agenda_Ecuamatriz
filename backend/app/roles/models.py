"""
app/roles/models.py — Modelo de datos: Role
Agenda Ecuamatriz
"""

from app import db


class Role(db.Model):
    """
    Rol del sistema.

    Slugs definidos (no cambiar sin refactorizar decoradores):
        - admin:     Administrador técnico-operativo.
        - secretary: Secretaría institucional.
        - user:      Colaborador interno.
    """

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)         # Nombre legible
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Identificador
    description = db.Column(db.Text, nullable=True)

    # ─── Relaciones ──────────────────────────────────────────────────────────
    users = db.relationship("User", back_populates="role", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Role id={self.id} slug={self.slug}>"


# ─── Constantes de slugs de rol ──────────────────────────────────────────────
# Usar estas constantes en decoradores y validaciones, no strings directos.
class RoleSlug:
    ADMIN = "admin"
    SECRETARY = "secretary"
    USER = "user"

    ALL = [ADMIN, SECRETARY, USER]
