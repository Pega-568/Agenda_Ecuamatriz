"""Rutas de notificaciones internas."""

from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.notifications.service import NotificationService
from app.shared.responses import error_response, success_response

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/", methods=["GET"])
@jwt_required()
def list_notifications():
    notifications = NotificationService.list_for_user(int(get_jwt_identity()))
    return success_response(data={"items": [NotificationService.to_dict(n) for n in notifications]})


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@jwt_required()
def mark_notification_read(notification_id):
    try:
        notification = NotificationService.mark_as_read(notification_id, int(get_jwt_identity()))
        return success_response(data=NotificationService.to_dict(notification))
    except ValueError as exc:
        return error_response(str(exc), 404, "NOTIFICATION_NOT_FOUND")
