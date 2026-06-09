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
        meetings = MeetingService.list_for_user(user, filters, mobile_context=True)
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
        meetings = MeetingService.list_for_user(user, filters, mobile_context=True)
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
        meetings = MeetingService.list_for_user(user, filters, mobile_context=True)
        return success_response(data=[MeetingService.to_dict(m) for m in meetings])
    except PermissionError as e:
        return error_response(str(e), 403)

@mobile_meetings_bp.route("", methods=["GET"])
@jwt_required()
def get_unified_agenda():
    """GET /api/mobile/meetings"""
    try:
        user = _current_user()
        filters = {"date_from": date.today()}
        meetings = MeetingService.list_for_user(user, filters, mobile_context=True)
        return success_response(data=[MeetingService.to_dict(m) for m in meetings])
    except PermissionError as e:
        return error_response(str(e), 403)

@mobile_meetings_bp.route("/options", methods=["GET"])
@jwt_required()
def get_meeting_options():
    """GET /api/mobile/meetings/options"""
    from app.rooms.models import Room
    from app.users.models import User
    from app.roles.models import Role, RoleSlug
    from app import db
    try:
        current_user = _current_user()
        rooms = db.session.query(Room).filter_by(is_active=True).all()
        users = db.session.query(User).filter(User.is_active == True, User.id != current_user.id, User.role.has(Role.slug != RoleSlug.ADMIN)).all()
        return success_response(data={
            "rooms": [{"id": r.id, "name": r.name, "location": r.location} for r in rooms],
            "users": [{"id": u.id, "name": u.full_name, "email": u.email, "area": u.area.name if u.area else None} for u in users]
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(str(e), 400)

@mobile_meetings_bp.route("", methods=["POST"])
@jwt_required()
def create_meeting():
    """POST /api/mobile/meetings"""
    from datetime import datetime
    try:
        user = _current_user()
        payload = request.get_json(silent=True) or {}
        
        # We need to parse dates
        date_str = payload.get("date")
        start_time_str = payload.get("start_time")
        end_time_str = payload.get("end_time")
        
        if not date_str or not start_time_str or not end_time_str:
             return error_response("Faltan campos obligatorios.", 400)
             
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
        
        data = {
            "title": payload.get("title"),
            "objective": payload.get("objective"),
            "description": payload.get("description"),
            "agenda_items": "\n".join(payload.get("agenda_items", [])),
            "date": date_obj,
            "start_time": start_time_obj,
            "end_time": end_time_obj,
            "modality": payload.get("modality", "virtual"),
            "room_id": payload.get("room_id"),
            "participant_ids": payload.get("participant_ids", []),
            "virtual_link": None
        }
        
        meeting, conflicts = MeetingService.create_meeting(user, data)
        if conflicts and conflicts.get("hard_blocks"):
             return error_response("Error de disponibilidad: la sala o un participante están ocupados.", 409)
             
        return success_response(data={"meeting": MeetingService.to_dict(meeting)}, message="Reunión creada correctamente.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(str(e), 400)

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
