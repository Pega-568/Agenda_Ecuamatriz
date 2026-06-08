"""
app/technical_sheets/routes.py — Rutas del módulo Technical Sheets
Agenda Ecuamatriz

Endpoints:
    GET  /api/technical-sheets/<meeting_id>   — Ver ficha técnica de reunión
    POST /api/technical-sheets/<meeting_id>   — Crear ficha técnica (creador)
    PUT  /api/technical-sheets/<meeting_id>   — Editar ficha (creador, estado draft)
    PUT  /api/technical-sheets/<meeting_id>/finalize — Finalizar ficha

Fase de implementación: Fase 5
"""

from flask import Blueprint

technical_sheets_bp = Blueprint("technical_sheets", __name__)


@technical_sheets_bp.route("/<int:meeting_id>", methods=["GET"])
def get_technical_sheet(meeting_id):
    """TODO (Fase 5): Ver ficha técnica de una reunión."""
    from app.shared.responses import error_response
    return error_response("Módulo technical_sheets — implementación pendiente (Fase 5).", 501)


@technical_sheets_bp.route("/<int:meeting_id>", methods=["POST"])
def create_technical_sheet(meeting_id):
    """TODO (Fase 5): Crear ficha técnica para reunión realizada."""
    from app.shared.responses import error_response
    return error_response("Módulo technical_sheets — implementación pendiente (Fase 5).", 501)


@technical_sheets_bp.route("/<int:meeting_id>", methods=["PUT"])
def update_technical_sheet(meeting_id):
    """TODO (Fase 5): Editar ficha técnica en estado draft."""
    from app.shared.responses import error_response
    return error_response("Módulo technical_sheets — implementación pendiente (Fase 5).", 501)


@technical_sheets_bp.route("/<int:meeting_id>/finalize", methods=["PUT"])
def finalize_technical_sheet(meeting_id):
    """TODO (Fase 5): Finalizar y cerrar ficha técnica."""
    from app.shared.responses import error_response
    return error_response("Módulo technical_sheets — implementación pendiente (Fase 5).", 501)
