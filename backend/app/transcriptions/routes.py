"""
app/transcriptions/routes.py — Rutas del módulo Transcriptions (FASE 8 FUTURO)
Agenda Ecuamatriz

⚠️  MÓDULO FUTURO — No implementar hasta Fase 8.
    Endpoints reservados para cuando el módulo de transcripción esté disponible.

Endpoints planificados:
    POST /api/transcriptions/<meeting_id>        — Solicitar transcripción
    GET  /api/transcriptions/<meeting_id>        — Ver transcripción
    GET  /api/transcriptions/<meeting_id>/draft  — Ver borrador de ficha técnica generado
"""

from flask import Blueprint

transcriptions_bp = Blueprint("transcriptions", __name__)


@transcriptions_bp.route("/<int:meeting_id>", methods=["POST"])
def request_transcription(meeting_id):
    """FUTURO (Fase 8): Solicitar transcripción de grabación."""
    from app.shared.responses import error_response
    return error_response("Módulo transcriptions — pendiente de implementación (Fase 8).", 501)


@transcriptions_bp.route("/<int:meeting_id>", methods=["GET"])
def get_transcription(meeting_id):
    """FUTURO (Fase 8): Obtener transcripción de reunión."""
    from app.shared.responses import error_response
    return error_response("Módulo transcriptions — pendiente de implementación (Fase 8).", 501)


@transcriptions_bp.route("/<int:meeting_id>/draft", methods=["GET"])
def get_transcription_draft(meeting_id):
    """FUTURO (Fase 8): Obtener borrador de ficha técnica generado desde transcripción."""
    from app.shared.responses import error_response
    return error_response("Módulo transcriptions — pendiente de implementación (Fase 8).", 501)
