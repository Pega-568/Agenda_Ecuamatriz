"""Servicios de usuarios."""

from sqlalchemy import or_

from app import bcrypt, db
from app.areas.models import Area
from app.roles.models import Role, RoleSlug
from app.users.models import User


class UserService:
    @staticmethod
    def get_by_id(user_id: int | str) -> User | None:
        return db.session.get(User, int(user_id))

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return User.query.filter_by(email=email.strip().lower()).first()

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @staticmethod
    def check_password(user: User, password: str) -> bool:
        return bcrypt.check_password_hash(user.password_hash, password)

    @staticmethod
    def create_user(data: dict) -> User:
        email = data["email"].strip().lower()
        if UserService.get_by_email(email):
            raise ValueError("El email ya está registrado.")

        role = db.session.get(Role, data["role_id"])
        if not role:
            raise ValueError("Rol no encontrado.")

        area_id = data.get("area_id")
        if area_id and not db.session.get(Area, area_id):
            raise ValueError("Área no encontrada.")

        full_name = data.get("full_name", "").strip()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        if full_name and not first_name:
            parts = full_name.split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

        user = User(
            first_name=(first_name or "").strip(),
            last_name=(last_name or "").strip(),
            email=email,
            password_hash=UserService.hash_password(data["password"]),
            role_id=role.id,
            area_id=area_id,
            phone=data.get("phone"),
            position=data.get("position"),
            is_active=data.get("is_active", True),
        )
        if not user.first_name or not user.last_name:
            raise ValueError("Nombre y apellido son obligatorios.")
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user_id: int, data: dict) -> User:
        user = UserService.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")

        if "email" in data:
            email = data["email"].strip().lower()
            existing = UserService.get_by_email(email)
            if existing and existing.id != user.id:
                raise ValueError("El email ya está registrado.")
            user.email = email

        for field in ["first_name", "last_name", "phone", "position"]:
            if field in data:
                setattr(user, field, data[field])

        if "full_name" in data and "first_name" not in data:
            parts = data["full_name"].strip().split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else user.last_name

        if "role_id" in data:
            if not db.session.get(Role, data["role_id"]):
                raise ValueError("Rol no encontrado.")
            user.role_id = data["role_id"]

        if "area_id" in data:
            area_id = data.get("area_id")
            if area_id and not db.session.get(Area, area_id):
                raise ValueError("Área no encontrada.")
            user.area_id = area_id

        if "password" in data and data["password"]:
            user.password_hash = UserService.hash_password(data["password"])

        db.session.commit()
        return user

    @staticmethod
    def set_active(user_id: int, is_active: bool) -> User:
        user = UserService.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")
        user.is_active = is_active
        db.session.commit()
        return user

    @staticmethod
    def search(
        query: str = "",
        area_id: int | None = None,
        active_only: bool = False,
        exclude_admin: bool = False,
        limit: int | None = None,
    ) -> list[User]:
        q = User.query
        if query:
            pattern = f"%{query.strip()}%"
            q = q.filter(or_(User.first_name.ilike(pattern), User.last_name.ilike(pattern), User.email.ilike(pattern)))
        if area_id:
            q = q.filter(User.area_id == area_id)
        if active_only:
            q = q.filter(User.is_active.is_(True))
        if exclude_admin:
            q = q.join(Role).filter(Role.slug != RoleSlug.ADMIN)
        q = q.order_by(User.first_name.asc(), User.last_name.asc())
        if limit:
            q = q.limit(limit)
        return q.all()

    @staticmethod
    def search_for_meetings(query: str = "", area_id: int | None = None, limit: int = 20) -> list[User]:
        return UserService.search(
            query=query,
            area_id=area_id,
            active_only=True,
            exclude_admin=True,
            limit=limit,
        )

    @staticmethod
    def to_dict(user: User) -> dict:
        return {
            "id": user.id,
            "full_name": user.full_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role_id": user.role_id,
            "role": user.role.slug if user.role else None,
            "area_id": user.area_id,
            "area": user.area.name if user.area else None,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }

    @staticmethod
    def to_search_item(user: User) -> dict:
        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "area": {"id": user.area.id, "name": user.area.name} if user.area else None,
            "role": user.role.slug if user.role else None,
        }
