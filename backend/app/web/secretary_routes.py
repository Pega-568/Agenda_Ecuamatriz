"""
Rutas web para secretaría
"""
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

web_secretary_bp = Blueprint("web_secretary", __name__, url_prefix="/secretary")

@web_secretary_bp.before_request
@login_required
def require_secretary():
    if current_user.role_slug != 'secretaria':
        abort(403)

@web_secretary_bp.route("/dashboard")
def dashboard():
    from app.meetings.service import MeetingService
    from datetime import date
    filters = {"date_from": date.today(), "date_to": date.today()}
    today_meetings = MeetingService.list_for_user(current_user, filters)
    return render_template("secretary/dashboard.html", today_meetings=today_meetings)

@web_secretary_bp.route("/meetings")
def meetings():
    from app.meetings.service import MeetingService
    meetings_list = MeetingService.list_for_user(current_user, {})
    return render_template("secretary/meetings.html", meetings=meetings_list)

@web_secretary_bp.route("/meetings/<int:meeting_id>")
def meeting_detail(meeting_id):
    from app.meetings.service import MeetingService
    try:
        meeting = MeetingService.get_detail(meeting_id, current_user)
        return render_template("secretary/meeting_detail.html", meeting=meeting)
    except ValueError:
        abort(404)
    except PermissionError:
        abort(403)

@web_secretary_bp.route("/meetings/<int:meeting_id>/attendance/manual", methods=["POST"])
def mark_manual_attendance(meeting_id):
    from app.attendance.service import AttendanceService
    from flask import request, flash, redirect, url_for
    
    user_id = int(request.form.get("user_id"))
    status = request.form.get("status")
    comment = request.form.get("comment", "")
    
    try:
        AttendanceService.mark_manual(meeting_id, current_user, user_id, status, comment=comment if comment else None)
        flash("Asistencia registrada manualmente.", "success")
    except Exception as e:
        flash(str(e), "danger")
        
    return redirect(url_for("web_secretary.meeting_detail", meeting_id=meeting_id))
