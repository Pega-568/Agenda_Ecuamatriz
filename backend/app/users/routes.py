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

from flask import Blueprint

users_bp = Blueprint("users", __name__)


@users_bp.route("/", methods=["GET"])
def list_users():
    """TODO (Fase 1): Listar usuarios. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo users — implementación pendiente (Fase 1).", 501)


@users_bp.route("/", methods=["POST"])
def create_user():
    """TODO (Fase 1): Crear usuario. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo users — implementación pendiente (Fase 1).", 501)


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """TODO (Fase 1): Detalle de usuario."""
    from app.shared.responses import error_response
    return error_response("Módulo users — implementación pendiente (Fase 1).", 501)


@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """TODO (Fase 1): Editar usuario. Admin o propietario."""
    from app.shared.responses import error_response
    return error_response("Módulo users — implementación pendiente (Fase 1).", 501)


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def deactivate_user(user_id):
    """TODO (Fase 1): Desactivar usuario. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo users — implementación pendiente (Fase 1).", 501)


@users_bp.route("/search", methods=["GET"])
def search_users():
    """TODO (Fase 1): Buscar usuarios por nombre/área para invitar a reunión."""
    from app.shared.responses import error_response
    return error_response("Módulo users — implementación pendiente (Fase 1).", 501)
