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

from flask import Blueprint, request

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/", methods=["GET"])
def list_rooms():
    """Lista salas activas."""
    from app.rooms.service import RoomService
    from app.shared.responses import success_response

    return success_response(data=[RoomService.to_dict(room) for room in RoomService.list_active()])


@rooms_bp.route("/", methods=["POST"])
def create_room():
    """Crea sala."""
    from marshmallow import ValidationError
    from app.rooms.schemas import RoomSchema
    from app.rooms.service import RoomService
    from app.shared.responses import created_response, error_response, validation_error_response

    try:
        payload = RoomSchema().load(request.get_json(silent=True) or {})
        room = RoomService.create_room(payload)
        return created_response(RoomService.to_dict(room))
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except (KeyError, ValueError) as exc:
        return error_response(str(exc), 422, "ROOM_VALIDATION_ERROR")


@rooms_bp.route("/<int:room_id>", methods=["GET"])
def get_room(room_id):
    """Detalle de sala."""
    from app import db
    from app.rooms.models import Room
    from app.rooms.service import RoomService
    from app.shared.responses import error_response, success_response

    room = db.session.get(Room, room_id)
    if not room:
        return error_response("Sala no encontrada.", 404, "ROOM_NOT_FOUND")
    return success_response(data=RoomService.to_dict(room))


@rooms_bp.route("/<int:room_id>", methods=["PUT"])
def update_room(room_id):
    """Edita sala."""
    from marshmallow import ValidationError
    from app.rooms.schemas import RoomSchema
    from app.rooms.service import RoomService
    from app.shared.responses import error_response, success_response, validation_error_response

    try:
        payload = RoomSchema(partial=True).load(request.get_json(silent=True) or {})
        room = RoomService.update_room(room_id, payload)
        return success_response(data=RoomService.to_dict(room))
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except ValueError as exc:
        return error_response(str(exc), 422, "ROOM_VALIDATION_ERROR")


@rooms_bp.route("/<int:room_id>", methods=["DELETE"])
def delete_room(room_id):
    """Desactiva sala."""
    from app.rooms.service import RoomService
    from app.shared.responses import error_response, success_response

    try:
        room = RoomService.set_active(room_id, False)
        return success_response(data=RoomService.to_dict(room))
    except ValueError as exc:
        return error_response(str(exc), 404, "ROOM_NOT_FOUND")
