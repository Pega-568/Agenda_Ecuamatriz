from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date, timedelta
from app.meetings.service import MeetingService
from app.users.service import UserService
from app.shared.responses import success_response, error_response

mobile_meetings_bp = Blueprint("mobile_meetings", __name__)

def _current_user():
    user = UserService.get_by_id(get_jwt_identity())
    if not user:
        raise PermissionError("Usuario no autenticado.")
    return user

@mobile_meetings_bp.route("/today", methods=["GET"])
@jwt_required()
def get_today_meetings():
    """GET /api/mobile/meetings/today"""
    try:
        user = _current_user()
        filters = {"date_from": date.today(), "date_to": date.today()}
        meetings = MeetingService.list_for_user(user, filters)
        return success_response(data=[MeetingService.to_dict(m) for m in meetings])
    except PermissionError as e:
        return error_response(str(e), 403)

@mobile_meetings_bp.route("/upcoming", methods=["GET"])
@jwt_required()
def get_upcoming_meetings():
    """GET /api/mobile/meetings/upcoming"""
    try:
        user = _current_user()
        filters = {"date_from": date.today() + timedelta(days=1)}
        meetings = MeetingService.list_for_user(user, filters)
        return success_response(data=[MeetingService.to_dict(m) for m in meetings])
    except PermissionError as e:
        return error_response(str(e), 403)

@mobile_meetings_bp.route("/invitations", methods=["GET"])
@jwt_required()
def get_invitations():
    """GET /api/mobile/meetings/invitations"""
    try:
        user = _current_user()
        filters = {"invited": True, "pending_response": True, "date_from": date.today()}
        meetings = MeetingService.list_for_user(user, filters)
        return success_response(data=[MeetingService.to_dict(m) for m in meetings])
    except PermissionError as e:
        return error_response(str(e), 403)

@mobile_meetings_bp.route("/<int:meeting_id>", methods=["GET"])
@jwt_required()
def get_meeting_detail(meeting_id):
    """GET /api/mobile/meetings/<id>"""
    try:
        meeting = MeetingService.get_detail(meeting_id, _current_user())
        return success_response(data=MeetingService.to_dict(meeting))
    except PermissionError as e:
        return error_response(str(e), 403)
    except ValueError as e:
        return error_response(str(e), 404)

@mobile_meetings_bp.route("/<int:meeting_id>/accept", methods=["POST"])
@jwt_required()
def accept_invitation(meeting_id):
    """POST /api/mobile/meetings/<id>/accept"""
    try:
        participant = MeetingService.accept(meeting_id, _current_user())
        return success_response(data={"invitation_status": participant.invitation_status})
    except PermissionError as e:
        return error_response(str(e), 403)
    except ValueError as e:
        return error_response(str(e), 409)

@mobile_meetings_bp.route("/<int:meeting_id>/reject", methods=["POST"])
@jwt_required()
def reject_invitation(meeting_id):
    """POST /api/mobile/meetings/<id>/reject"""
    try:
        payload = request.get_json(silent=True) or {}
        participant = MeetingService.reject(meeting_id, _current_user(), payload.get("comment"))
        return success_response(data={"invitation_status": participant.invitation_status})
    except PermissionError as e:
        return error_response(str(e), 403)
    except ValueError as e:
        return error_response(str(e), 409)
