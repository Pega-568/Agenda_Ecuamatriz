"""
app/rooms/routes.py — Rutas del módulo Rooms
Agenda Ecuamatriz

Endpoints:
    GET    /api/rooms/       — Listar salas
    POST   /api/rooms/       — Crear sala (Admin)
    GET    /api/rooms/<id>   — Detalle de sala
    PUT    /api/rooms/<id>   — Editar sala (Admin)
    DELETE /api/rooms/<id>   — Eliminar sala (Admin)

Fase de implementación: Fase 1
"""

from flask import Blueprint

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/", methods=["GET"])
def list_rooms():
    """TODO (Fase 1): Listar salas disponibles."""
    from app.shared.responses import error_response
    return error_response("Módulo rooms — implementación pendiente (Fase 1).", 501)


@rooms_bp.route("/", methods=["POST"])
def create_room():
    """TODO (Fase 1): Crear sala. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo rooms — implementación pendiente (Fase 1).", 501)


@rooms_bp.route("/<int:room_id>", methods=["GET"])
def get_room(room_id):
    """TODO (Fase 1): Detalle de sala."""
    from app.shared.responses import error_response
    return error_response("Módulo rooms — implementación pendiente (Fase 1).", 501)


@rooms_bp.route("/<int:room_id>", methods=["PUT"])
def update_room(room_id):
    """TODO (Fase 1): Editar sala. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo rooms — implementación pendiente (Fase 1).", 501)


@rooms_bp.route("/<int:room_id>", methods=["DELETE"])
def delete_room(room_id):
    """TODO (Fase 1): Eliminar sala. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo rooms — implementación pendiente (Fase 1).", 501)
