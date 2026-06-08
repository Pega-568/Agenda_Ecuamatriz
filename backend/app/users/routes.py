"""
app/users/routes.py — Rutas del módulo Users
Agenda Ecuamatriz

Endpoints:
    GET    /api/users/           — Listar usuarios (Admin)
    POST   /api/users/           — Crear usuario (Admin)
    GET    /api/users/<id>       — Detalle de usuario
    PUT    /api/users/<id>       — Editar usuario (Admin o propietario)
    DELETE /api/users/<id>       — Desactivar usuario (Admin)
    GET    /api/users/search     — Buscar usuarios para invitación (autenticado)

Fase de implementación: Fase 1
"""

from flask import Blueprint, request

users_bp = Blueprint("users", __name__)


@users_bp.route("/", methods=["GET"])
def list_users():
    """Lista usuarios."""
    from app.shared.responses import success_response
    from app.users.service import UserService

    users = UserService.search(request.args.get("q", ""), request.args.get("area_id", type=int))
    return success_response(data=[UserService.to_dict(user) for user in users])


@users_bp.route("/", methods=["POST"])
def create_user():
    """Crea usuario."""
    from marshmallow import ValidationError
    from app.shared.responses import created_response, error_response, validation_error_response
    from app.users.schemas import UserCreateSchema
    from app.users.service import UserService

    try:
        payload = UserCreateSchema().load(request.get_json(silent=True) or {})
        user = UserService.create_user(payload)
        return created_response(UserService.to_dict(user))
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except (KeyError, ValueError) as exc:
        return error_response(str(exc), 422, "USER_VALIDATION_ERROR")


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Detalle de usuario."""
    from app.shared.responses import error_response, success_response
    from app.users.service import UserService

    user = UserService.get_by_id(user_id)
    if not user:
        return error_response("Usuario no encontrado.", 404, "USER_NOT_FOUND")
    return success_response(data=UserService.to_dict(user))


@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Edita usuario."""
    from marshmallow import ValidationError
    from app.shared.responses import error_response, success_response, validation_error_response
    from app.users.schemas import UserUpdateSchema
    from app.users.service import UserService

    try:
        payload = UserUpdateSchema().load(request.get_json(silent=True) or {})
        user = UserService.update_user(user_id, payload)
        return success_response(data=UserService.to_dict(user))
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except ValueError as exc:
        return error_response(str(exc), 422, "USER_VALIDATION_ERROR")


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def deactivate_user(user_id):
    """Desactiva usuario."""
    from app.shared.responses import error_response, success_response
    from app.users.service import UserService

    try:
        user = UserService.set_active(user_id, False)
        return success_response(data=UserService.to_dict(user))
    except ValueError as exc:
        return error_response(str(exc), 404, "USER_NOT_FOUND")


@users_bp.route("/search", methods=["GET"])
def search_users():
    """Busca usuarios por nombre, correo o área."""
    from app.shared.responses import success_response
    from app.users.service import UserService

    users = UserService.search(request.args.get("q", ""), request.args.get("area_id", type=int))
    return success_response(data=[UserService.to_dict(user) for user in users])
