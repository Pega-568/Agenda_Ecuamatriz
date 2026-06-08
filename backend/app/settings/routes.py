"""
app/settings/routes.py — Rutas del módulo System Settings
Agenda Ecuamatriz

Endpoints:
    GET /api/settings/          — Ver configuración actual (Admin)
    PUT /api/settings/          — Actualizar configuración (Admin)
    GET /api/settings/public    — Ver parámetros públicos (autenticado)

Fase de implementación: Fase 1
"""

from flask import Blueprint, request

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/", methods=["GET"])
def get_settings():
    """Lista configuración."""
    from app.settings.service import SettingsService
    from app.shared.responses import success_response

    SettingsService.seed_defaults()
    return success_response(data={s.key: SettingsService.to_dict(s) for s in SettingsService.list_settings()})


@settings_bp.route("/", methods=["PUT"])
def update_settings():
    """Actualiza configuración."""
    from marshmallow import ValidationError
    from app.settings.schemas import SettingsUpdateSchema
    from app.settings.service import SettingsService
    from app.shared.responses import error_response, success_response, validation_error_response

    try:
        payload = SettingsUpdateSchema().load(request.get_json(silent=True) or {})
        settings = SettingsService.update_settings(payload)
        return success_response(data={s.key: SettingsService.to_dict(s) for s in settings})
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except ValueError as exc:
        return error_response(str(exc), 422, "SETTING_VALIDATION_ERROR")


@settings_bp.route("/public", methods=["GET"])
def get_public_settings():
    """Parámetros públicos básicos."""
    from app.settings.service import SettingsService
    from app.shared.responses import success_response

    SettingsService.seed_defaults()
    public_keys = [
        "max_meeting_participants",
        "max_meeting_duration_minutes",
        "min_meeting_notice_minutes",
        "web_notifications_enabled",
    ]
    data = {
        s.key: SettingsService.to_dict(s)
        for s in SettingsService.list_settings()
        if s.key in public_keys
    }
    return success_response(data=data)
