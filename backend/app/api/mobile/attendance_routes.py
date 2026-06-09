from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.attendance.service import AttendanceService
from app.users.service import UserService
from app.shared.responses import success_response, error_response

mobile_attendance_bp = Blueprint("mobile_attendance", __name__)

def _current_user():
    user = UserService.get_by_id(get_jwt_identity())
    if not user:
        raise PermissionError("Usuario no autenticado.")
    return user

@mobile_attendance_bp.route("/qr/<token>", methods=["POST"])
@jwt_required()
def mark_attendance_qr(token):
    """POST /api/mobile/attendance/qr/<token>"""
    try:
        participant = AttendanceService.mark_qr(token, _current_user())
        return success_response(
            message="Asistencia marcada con éxito.",
            data=AttendanceService.participant_to_dict(participant)
        )
    except PermissionError as e:
        return error_response(str(e), 403)
    except ValueError as e:
        return error_response(str(e), 409)

@mobile_attendance_bp.route("/meeting/<int:meeting_id>/my-status", methods=["GET"])
@jwt_required()
def get_my_status(meeting_id):
    """GET /api/mobile/attendance/meeting/<int:meeting_id>/my-status"""
    try:
        user = _current_user()
        from app.meetings.models import MeetingParticipant
        participant = MeetingParticipant.query.filter_by(meeting_id=meeting_id, user_id=user.id).first()
        if not participant:
            return error_response("No eres participante de esta reunión.", 404)
        return success_response(data=AttendanceService.participant_to_dict(participant))
    except PermissionError as e:
        return error_response(str(e), 403)
