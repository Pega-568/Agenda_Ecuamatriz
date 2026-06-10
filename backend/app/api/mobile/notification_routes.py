from flask import Blueprint, request
from app.shared.responses import success_response, error_response
from app.notifications.service import NotificationService
from app.users.service import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity

mobile_notifications_bp = Blueprint("mobile_notifications", __name__)

@mobile_notifications_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications():
    """
    GET /api/mobile/notifications
    Retorna la lista de notificaciones del usuario autenticado.
    """
    user = UserService.get_by_id(get_jwt_identity())
    if not user:
        return error_response("Usuario no encontrado.", 404)
        
    static_notifications = NotificationService.list_for_user(user.id)
    static_list = [NotificationService.to_dict(n) for n in static_notifications]
    
    dynamic_list = NotificationService.get_dynamic_notifications(user)
    
    all_notifications = static_list + dynamic_list
    all_notifications.sort(key=lambda x: x["created_at"], reverse=True)
    
    return success_response(
        data=all_notifications,
        message="Notificaciones obtenidas."
    )

@mobile_notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@jwt_required()
def mark_notification_read(notification_id):
    """
    POST /api/mobile/notifications/<id>/read
    Marca una notificación como leída.
    """
    user_id = int(get_jwt_identity())
    try:
        notification = NotificationService.mark_as_read(notification_id, user_id)
        return success_response(
            data=NotificationService.to_dict(notification),
            message="Notificación marcada como leída."
        )
    except ValueError as e:
        return error_response(str(e), 404)
