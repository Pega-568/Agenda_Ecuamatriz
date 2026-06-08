"""Rutas de asistencia por QR."""

from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.attendance.service import AttendanceService
from app.shared.responses import error_response, success_response
from app.users.service import UserService

attendance_bp = Blueprint("attendance", __name__)


def _current_user():
    user = UserService.get_by_id(get_jwt_identity())
    if not user:
        raise PermissionError("Usuario no autenticado.")
    return user


@attendance_bp.route("/qr/<path:token>", methods=["POST"])
@jwt_required()
def mark_qr_attendance(token):
    """Marca asistencia de un participante mediante QR fijo."""
    try:
        participant = AttendanceService.mark_by_qr(token, _current_user())
        return success_response(
            data={
                "status": "ok",
                "message": "Asistencia registrada correctamente",
                "meeting_id": participant.meeting_id,
                "attendance_status": participant.attendance_status,
                "attendance_method": participant.attendance_method,
            }
        )
    except PermissionError as exc:
        return error_response(str(exc), 403, "FORBIDDEN")
    except ValueError as exc:
        return error_response(str(exc), 409, "QR_ATTENDANCE_ERROR")
