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

from flask import Blueprint

areas_bp = Blueprint("areas", __name__)


@areas_bp.route("/", methods=["GET"])
def list_areas():
    """TODO (Fase 1): Listar áreas."""
    from app.shared.responses import error_response
    return error_response("Módulo areas — implementación pendiente (Fase 1).", 501)


@areas_bp.route("/", methods=["POST"])
def create_area():
    """TODO (Fase 1): Crear área. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo areas — implementación pendiente (Fase 1).", 501)


@areas_bp.route("/<int:area_id>", methods=["GET"])
def get_area(area_id):
    """TODO (Fase 1): Detalle de área."""
    from app.shared.responses import error_response
    return error_response("Módulo areas — implementación pendiente (Fase 1).", 501)


@areas_bp.route("/<int:area_id>", methods=["PUT"])
def update_area(area_id):
    """TODO (Fase 1): Editar área. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo areas — implementación pendiente (Fase 1).", 501)


@areas_bp.route("/<int:area_id>", methods=["DELETE"])
def delete_area(area_id):
    """TODO (Fase 1): Eliminar área. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo areas — implementación pendiente (Fase 1).", 501)
