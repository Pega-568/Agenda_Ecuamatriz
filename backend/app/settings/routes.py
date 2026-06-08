"""
app/settings/routes.py — Rutas del módulo System Settings
Agenda Ecuamatriz

Endpoints:
    GET /api/settings/          — Ver configuración actual (Admin)
    PUT /api/settings/          — Actualizar configuración (Admin)
    GET /api/settings/public    — Ver parámetros públicos (autenticado)

Fase de implementación: Fase 1
"""

from flask import Blueprint

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/", methods=["GET"])
def get_settings():
    """TODO (Fase 1): Ver configuración del sistema. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo settings — implementación pendiente (Fase 1).", 501)


@settings_bp.route("/", methods=["PUT"])
def update_settings():
    """TODO (Fase 1): Actualizar configuración. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo settings — implementación pendiente (Fase 1).", 501)


@settings_bp.route("/public", methods=["GET"])
def get_public_settings():
    """TODO (Fase 1): Ver parámetros públicos como horario laboral. Autenticado."""
    from app.shared.responses import error_response
    return error_response("Módulo settings — implementación pendiente (Fase 1).", 501)
