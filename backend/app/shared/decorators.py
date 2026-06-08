"""
app/shared/decorators.py — Decoradores de autorización y permisos
Agenda Ecuamatriz

Uso en routes:
    from app.shared.decorators import require_role, require_roles

    @meetings_bp.route("/", methods=["POST"])
    @jwt_required()
    @require_role("user")
    def create_meeting():
        ...

    @admin_bp.route("/users", methods=["GET"])
    @jwt_required()
    @require_role("admin")
    def list_users():
        ...
"""

from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.shared.responses import error_response


def require_role(*allowed_roles: str):
    """
    Decorador que verifica que el usuario autenticado tenga uno de los roles permitidos.

    Args:
        *allowed_roles: Roles permitidos (ej: "admin", "secretary", "user").
                        Valores válidos definidos en app/roles/constants.py

    Uso:
        @require_role("admin")           # Solo admin
        @require_role("admin", "secretary")  # Admin o secretaría

    IMPORTANTE: Debe usarse después de @jwt_required().
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Obtener identidad del JWT (user_id)
            user_id = get_jwt_identity()
            if not user_id:
                return error_response("Token inválido.", 401, "INVALID_TOKEN")

            # Importación local para evitar circular imports
            from app.users.service import UserService
            user = UserService.get_by_id(user_id)

            if not user:
                return error_response("Usuario no encontrado.", 404, "USER_NOT_FOUND")

            if not user.role or user.role.slug not in allowed_roles:
                return error_response(
                    "No tienes permisos para realizar esta acción.",
                    403,
                    "FORBIDDEN",
                )

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_self_or_role(param_name: str = "user_id", *admin_roles: str):
    """
    Decorador que permite acceso si el usuario es dueño del recurso
    o tiene un rol administrativo.

    Args:
        param_name: Nombre del parámetro de URL que contiene el user_id del recurso.
        *admin_roles: Roles que pueden acceder a cualquier recurso.

    Uso:
        @require_self_or_role("user_id", "admin")
        def get_user_profile(user_id):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            target_user_id = kwargs.get(param_name)

            # Permitir si es el propio usuario
            if str(current_user_id) == str(target_user_id):
                return fn(*args, **kwargs)

            # Permitir si tiene rol administrativo
            from app.users.service import UserService
            user = UserService.get_by_id(current_user_id)

            if user and user.role and user.role.slug in (admin_roles or ["admin"]):
                return fn(*args, **kwargs)

            return error_response(
                "No tienes permisos para acceder a este recurso.",
                403,
                "FORBIDDEN",
            )
        return wrapper
    return decorator
