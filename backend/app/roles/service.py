"""Servicios de roles."""

from app import db
from app.roles.models import Role, RoleSlug


class RoleService:
    DEFAULT_ROLES = [
        {
            "slug": RoleSlug.ADMIN,
            "name": "Administrador",
            "description": "Gestiona usuarios, salas, areas y configuracion.",
        },
        {
            "slug": RoleSlug.SECRETARY,
            "name": "Secretaria",
            "description": "Gestiona calendario institucional y soporte operativo.",
        },
        {
            "slug": RoleSlug.USER,
            "name": "Usuario",
            "description": "Colaborador interno del sistema.",
        },
    ]

    @staticmethod
    def seed_defaults() -> list[Role]:
        roles = []
        for data in RoleService.DEFAULT_ROLES:
            role = Role.query.filter_by(slug=data["slug"]).first()
            if role:
                role.name = data["name"]
                role.description = data["description"]
            else:
                role = Role(**data)
                db.session.add(role)
            roles.append(role)
        db.session.commit()
        return roles

    @staticmethod
    def list_roles() -> list[Role]:
        return Role.query.order_by(Role.id.asc()).all()

    @staticmethod
    def get_by_slug(slug: str) -> Role | None:
        return Role.query.filter_by(slug=slug).first()

    @staticmethod
    def get_by_name(name: str) -> Role | None:
        return Role.query.filter(Role.name.ilike(name.strip())).first()

    @staticmethod
    def to_dict(role: Role) -> dict:
        return {
            "id": role.id,
            "slug": role.slug,
            "name": role.name,
            "description": role.description,
        }
