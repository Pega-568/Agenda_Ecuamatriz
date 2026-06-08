"""
app/areas/routes.py — Rutas del módulo Areas
Agenda Ecuamatriz

Endpoints:
    GET    /api/areas/       — Listar áreas
    POST   /api/areas/       — Crear área (Admin)
    GET    /api/areas/<id>   — Detalle de área
    PUT    /api/areas/<id>   — Editar área (Admin)
    DELETE /api/areas/<id>   — Eliminar área (Admin)

Fase de implementación: Fase 1
"""

from flask import Blueprint, request

areas_bp = Blueprint("areas", __name__)


@areas_bp.route("/", methods=["GET"])
def list_areas():
    """Lista áreas activas."""
    from app.areas.service import AreaService
    from app.shared.responses import success_response

    return success_response(data=[AreaService.to_dict(area) for area in AreaService.list_active()])


@areas_bp.route("/", methods=["POST"])
def create_area():
    """Crea área."""
    from marshmallow import ValidationError
    from app.areas.schemas import AreaSchema
    from app.areas.service import AreaService
    from app.shared.responses import created_response, error_response, validation_error_response

    try:
        payload = AreaSchema().load(request.get_json(silent=True) or {})
        area = AreaService.create_area(payload)
        return created_response(AreaService.to_dict(area))
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except (KeyError, ValueError) as exc:
        return error_response(str(exc), 422, "AREA_VALIDATION_ERROR")


@areas_bp.route("/<int:area_id>", methods=["GET"])
def get_area(area_id):
    """Detalle de área."""
    from app import db
    from app.areas.models import Area
    from app.areas.service import AreaService
    from app.shared.responses import error_response, success_response

    area = db.session.get(Area, area_id)
    if not area:
        return error_response("Área no encontrada.", 404, "AREA_NOT_FOUND")
    return success_response(data=AreaService.to_dict(area))


@areas_bp.route("/<int:area_id>", methods=["PUT"])
def update_area(area_id):
    """Edita área."""
    from marshmallow import ValidationError
    from app.areas.schemas import AreaSchema
    from app.areas.service import AreaService
    from app.shared.responses import error_response, success_response, validation_error_response

    try:
        payload = AreaSchema(partial=True).load(request.get_json(silent=True) or {})
        area = AreaService.update_area(area_id, payload)
        return success_response(data=AreaService.to_dict(area))
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except ValueError as exc:
        return error_response(str(exc), 422, "AREA_VALIDATION_ERROR")


@areas_bp.route("/<int:area_id>", methods=["DELETE"])
def delete_area(area_id):
    """Desactiva área."""
    from app.areas.service import AreaService
    from app.shared.responses import error_response, success_response

    try:
        area = AreaService.set_active(area_id, False)
        return success_response(data=AreaService.to_dict(area))
    except ValueError as exc:
        return error_response(str(exc), 404, "AREA_NOT_FOUND")
