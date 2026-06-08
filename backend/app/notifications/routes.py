"""
app/notifications/routes.py — Rutas del módulo Notifications
Agenda Ecuamatriz

Endpoints:
    GET  /api/notifications/          — Mis notificaciones (autenticado)
    PUT  /api/notifications/<id>/read — Marcar notificación como leída
    PUT  /api/notifications/read-all  — Marcar todas como leídas
    GET  /api/notifications/unread-count — Contador de no leídas

Fase de implementación: Fase 2 (base web), Fase 7 (FCM Android)
"""

from flask import Blueprint

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/", methods=["GET"])
def list_notifications():
    """TODO (Fase 2): Listar notificaciones del usuario autenticado."""
    from app.shared.responses import error_response
    return error_response("Módulo notifications — implementación pendiente (Fase 2).", 501)


@notifications_bp.route("/<int:notification_id>/read", methods=["PUT"])
def mark_as_read(notification_id):
    """TODO (Fase 2): Marcar notificación como leída."""
    from app.shared.responses import error_response
    return error_response("Módulo notifications — implementación pendiente (Fase 2).", 501)


@notifications_bp.route("/read-all", methods=["PUT"])
def mark_all_as_read():
    """TODO (Fase 2): Marcar todas las notificaciones como leídas."""
    from app.shared.responses import error_response
    return error_response("Módulo notifications — implementación pendiente (Fase 2).", 501)


@notifications_bp.route("/unread-count", methods=["GET"])
def get_unread_count():
    """TODO (Fase 2): Obtener cantidad de notificaciones no leídas."""
    from app.shared.responses import error_response
    return error_response("Módulo notifications — implementación pendiente (Fase 2).", 501)
