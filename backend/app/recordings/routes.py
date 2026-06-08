"""
app/recordings/routes.py — Rutas del módulo Recordings (FASE 8 FUTURO)
Agenda Ecuamatriz

⚠️  MÓDULO FUTURO — No implementar hasta Fase 8.
    Endpoints reservados para cuando el módulo de grabación esté disponible.

Endpoints planificados:
    POST   /api/recordings/<meeting_id>        — Iniciar grabación
    GET    /api/recordings/<meeting_id>        — Ver grabación de reunión
    DELETE /api/recordings/<meeting_id>        — Eliminar grabación
"""

from flask import Blueprint

recordings_bp = Blueprint("recordings", __name__)


@recordings_bp.route("/<int:meeting_id>", methods=["POST"])
def start_recording(meeting_id):
    """FUTURO (Fase 8): Iniciar grabación de reunión."""
    from app.shared.responses import error_response
    return error_response("Módulo recordings — pendiente de implementación (Fase 8).", 501)


@recordings_bp.route("/<int:meeting_id>", methods=["GET"])
def get_recording(meeting_id):
    """FUTURO (Fase 8): Obtener grabación de reunión."""
    from app.shared.responses import error_response
    return error_response("Módulo recordings — pendiente de implementación (Fase 8).", 501)


@recordings_bp.route("/<int:meeting_id>", methods=["DELETE"])
def delete_recording(meeting_id):
    """FUTURO (Fase 8): Eliminar grabación de reunión."""
    from app.shared.responses import error_response
    return error_response("Módulo recordings — pendiente de implementación (Fase 8).", 501)
