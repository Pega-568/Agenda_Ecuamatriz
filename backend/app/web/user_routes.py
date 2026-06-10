"""
Rutas web para usuarios
"""
from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date

web_user_bp = Blueprint("web_user", __name__, url_prefix="/user")

@web_user_bp.before_request
@login_required
def require_user():
    if current_user.role_slug != 'usuario':
        abort(403)

@web_user_bp.route("/dashboard")
def dashboard():
    from app.meetings.service import MeetingService
    
    # Reuniones de hoy y pendientess usaremos el Service en lugar de queries manuales
    filters = {"date_from": date.today(), "date_to": date.today(), "status": "scheduled"}
    today_meetings = MeetingService.list_for_user(current_user, filters)
    
    # Filtro custom para invitaciones
    pending_filters = {"pending_response": True}
    pending_invitations_meetings = MeetingService.list_for_user(current_user, pending_filters)
    
    # Necesitamos pasar los objetos Invitation (participant) a la vista
    # ya que pending_invitations_meetings son reuniones, buscaremos el participant
    pending_invitations = []
    for m in pending_invitations_meetings:
        for p in m.participants:
            if p.user_id == current_user.id and p.invitation_status == 'pending':
                pending_invitations.append(p)

    return render_template("user/dashboard.html", today_meetings=today_meetings, pending_invitations=pending_invitations)

@web_user_bp.route("/meetings", methods=["GET"])
def meetings():
    from app.meetings.service import MeetingService
    meetings_list = MeetingService.list_for_user(current_user, {"created_by_me": True})
    return render_template("user/meetings.html", meetings=meetings_list)

@web_user_bp.route("/meetings/create", methods=["GET", "POST"])
def create_meeting():
    from app.rooms.models import Room
    from app.users.models import User
    from app.meetings.service import MeetingService
    from app import db
    from datetime import datetime
    
    if request.method == "POST":
        title = request.form.get("title")
        date_str = request.form.get("date")
        start_time_str = request.form.get("start_time")
        end_time_str = request.form.get("end_time")
        room_id = request.form.get("room_id")
        objective = request.form.get("objective")
        description = request.form.get("description", "")
        agenda_items_str = request.form.get("agenda_items", "")
        modality = request.form.get("modality", "in_person")
        
        # Parsear agenda
        agenda_items = [item.strip() for item in agenda_items_str.split(",") if item.strip()]
        
        # Parsear participants desde multiples inputs (checkboxes)
        participant_ids_str = request.form.getlist("participant_ids")
        participant_ids = [int(p) for p in participant_ids_str if p.strip().isdigit()]
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
            
            data = {
                "title": title,
                "objective": objective,
                "description": description,
                "agenda_items": agenda_items,
                "date": date_obj,
                "start_time": start_time_obj,
                "end_time": end_time_obj,
                "modality": modality,
                "room_id": int(room_id) if room_id else None,
                "participant_ids": participant_ids,
                "virtual_link": None
            }
            
            meeting, conflicts = MeetingService.create_meeting(current_user, data)
            
            if conflicts and conflicts.get("hard_blocks"):
                flash(f"Error de disponibilidad: la sala o un participante esencial están ocupados.", "danger")
            elif meeting:
                flash("Reunión creada exitosamente.", "success")
                return redirect(url_for("web_user.meetings"))
                
        except Exception as e:
            flash(f"Error al crear reunión: {str(e)}", "danger")
            
    rooms_list = db.session.query(Room).filter_by(is_active=True).all()
    # Fetch active users excluding admin and current user
    users_list = db.session.query(User).filter(User.is_active == True, User.role_slug != 'admin', User.id != current_user.id).all()
    return render_template("user/create_meeting.html", rooms=rooms_list, users=users_list)

@web_user_bp.route("/meetings/<int:meeting_id>")
def meeting_detail(meeting_id):
    from app.meetings.service import MeetingService
    try:
        meeting = MeetingService.get_detail(meeting_id, current_user)
        return render_template("user/meeting_detail.html", meeting=meeting)
    except ValueError:
        abort(404)
    except PermissionError:
        abort(403)

@web_user_bp.route("/meetings/<int:meeting_id>/qr")
def qr_display(meeting_id):
    from app.attendance.service import AttendanceService
    from app.meetings.service import MeetingService
    
    try:
        meeting = MeetingService.get_detail(meeting_id, current_user)
        result = AttendanceService.generate_or_get_attendance_token(meeting.id, current_user)
        
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={result['qr_payload']}"
        return render_template("user/qr_display.html", meeting=meeting, qr_image_url=qr_image_url, valid_until=result['valid_until'], qr_payload=result['qr_payload'])
    except Exception as e:
        flash(f"Error al generar QR: {str(e)}", "danger")
        return redirect(url_for("web_user.meeting_detail", meeting_id=meeting_id))

@web_user_bp.route("/meetings/<int:meeting_id>/action", methods=["POST"])
def action_meeting(meeting_id):
    from app.meetings.service import MeetingService
    
    action = request.form.get("action")
    comment = request.form.get("comment")
    
    try:
        if action == "accept":
            MeetingService.accept(meeting_id, current_user)
            flash("Invitación aceptada.", "success")
        elif action == "reject":
            MeetingService.reject(meeting_id, current_user, comment=comment)
            flash("Invitación rechazada.", "warning")
    except Exception as e:
        flash(str(e), "danger")
        
    return redirect(url_for("web_user.dashboard"))

@web_user_bp.route("/meetings/check-availability", methods=["POST"])
def check_availability():
    from app.availability.service import AvailabilityService
    from app.availability.schemas import AvailabilityCheckSchema
    from marshmallow import ValidationError
    from flask import jsonify
    
    try:
        payload = AvailabilityCheckSchema().load(request.get_json(silent=True) or {})
        result = AvailabilityService.check(payload, creator_id=current_user.id)
        return jsonify({"success": True, "data": result}), 200
    except ValidationError as exc:
        return jsonify({"success": False, "error": {"message": "Datos inválidos", "details": exc.messages}}), 422
    except Exception as exc:
        return jsonify({"success": False, "error": {"message": str(exc)}}), 400
