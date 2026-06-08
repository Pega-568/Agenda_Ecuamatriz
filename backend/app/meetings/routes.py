"""Rutas del módulo Meetings."""

from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from app.availability.schemas import AvailabilityCheckSchema
from app.availability.service import AvailabilityService
from app.meetings.schemas import MeetingCancelSchema, MeetingCreateSchema, MeetingRejectSchema
from app.meetings.service import MeetingService
from app.shared.responses import created_response, error_response, success_response, validation_error_response
from app.users.service import UserService

meetings_bp = Blueprint("meetings", __name__)


def _current_user():
    user = UserService.get_by_id(get_jwt_identity())
    if not user:
        raise PermissionError("Usuario no autenticado.")
    return user


@meetings_bp.route("/check-availability", methods=["POST"])
@jwt_required()
def check_availability():
    """Valida disponibilidad integrada para el flujo de nueva reunión."""
    try:
        payload = AvailabilityCheckSchema().load(request.get_json(silent=True) or {})
        result = AvailabilityService.check(payload, creator_id=_current_user().id)
        return success_response(data=result)
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except PermissionError as exc:
        return error_response(str(exc), 401, "UNAUTHORIZED")


@meetings_bp.route("", methods=["POST"])
@meetings_bp.route("/", methods=["POST"])
@jwt_required()
def create_meeting():
    """Crea reunión si no existen bloqueos duros de disponibilidad."""
    try:
        payload = MeetingCreateSchema().load(request.get_json(silent=True) or {})
        meeting, availability = MeetingService.create_meeting(_current_user(), payload)
        if not meeting:
            return error_response("La reunión no puede crearse por bloqueos de disponibilidad.", 409, "AVAILABILITY_BLOCKED", availability)
        return created_response(data={"meeting": MeetingService.to_dict(meeting), "availability": availability})
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except PermissionError as exc:
        return error_response(str(exc), 403, "FORBIDDEN")
    except ValueError as exc:
        return error_response(str(exc), 422, "MEETING_VALIDATION_ERROR")


@meetings_bp.route("", methods=["GET"])
@meetings_bp.route("/", methods=["GET"])
@jwt_required()
def list_meetings():
    """Lista reuniones relevantes para el usuario autenticado."""
    try:
        filters = {
            "date_from": _parse_date(request.args.get("date_from")),
            "date_to": _parse_date(request.args.get("date_to")),
            "status": request.args.get("status"),
            "created_by_me": request.args.get("created_by_me") == "true",
            "invited": request.args.get("invited") == "true",
            "pending_response": request.args.get("pending_response") == "true",
        }
        meetings = MeetingService.list_for_user(_current_user(), filters)
        return success_response(data={"items": [MeetingService.to_dict(meeting) for meeting in meetings]})
    except PermissionError as exc:
        return error_response(str(exc), 403, "FORBIDDEN")


@meetings_bp.route("/<int:meeting_id>", methods=["GET"])
@jwt_required()
def get_meeting(meeting_id):
    """Detalle de reunión."""
    try:
        meeting = MeetingService.get_detail(meeting_id, _current_user())
        return success_response(data=MeetingService.to_dict(meeting))
    except PermissionError as exc:
        return error_response(str(exc), 403, "FORBIDDEN")
    except ValueError as exc:
        return error_response(str(exc), 404, "MEETING_NOT_FOUND")


@meetings_bp.route("/<int:meeting_id>/accept", methods=["POST"])
@jwt_required()
def accept_meeting(meeting_id):
    """Acepta invitación a reunión."""
    try:
        participant = MeetingService.accept(meeting_id, _current_user())
        return success_response(data={"meeting_id": meeting_id, "invitation_status": participant.invitation_status})
    except PermissionError as exc:
        return error_response(str(exc), 403, "FORBIDDEN")
    except ValueError as exc:
        return error_response(str(exc), 409, "MEETING_ACCEPT_ERROR")


@meetings_bp.route("/<int:meeting_id>/reject", methods=["POST"])
@jwt_required()
def reject_meeting(meeting_id):
    """Rechaza invitación a reunión."""
    try:
        payload = MeetingRejectSchema().load(request.get_json(silent=True) or {})
        participant = MeetingService.reject(meeting_id, _current_user(), payload.get("comment"))
        return success_response(data={"meeting_id": meeting_id, "invitation_status": participant.invitation_status})
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except PermissionError as exc:
        return error_response(str(exc), 403, "FORBIDDEN")
    except ValueError as exc:
        return error_response(str(exc), 409, "MEETING_REJECT_ERROR")


@meetings_bp.route("/<int:meeting_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_meeting(meeting_id):
    """Cancela reunión."""
    try:
        payload = MeetingCancelSchema().load(request.get_json(silent=True) or {})
        meeting = MeetingService.cancel(meeting_id, _current_user(), payload.get("reason"))
        return success_response(data=MeetingService.to_dict(meeting))
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except PermissionError as exc:
        return error_response(str(exc), 403, "FORBIDDEN")
    except ValueError as exc:
        return error_response(str(exc), 409, "MEETING_CANCEL_ERROR")


def _parse_date(value: str | None):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()
