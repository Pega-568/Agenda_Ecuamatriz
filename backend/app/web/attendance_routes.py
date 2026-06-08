"""
Rutas web para validación de asistencia vía QR.
"""
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.attendance.service import AttendanceService

web_attendance_bp = Blueprint("web_attendance", __name__, url_prefix="/attendance")

@web_attendance_bp.route("/qr/<string:plain_token>")
@login_required
def mark_attendance_qr(plain_token):
    try:
        participant = AttendanceService.mark_by_qr(plain_token, current_user)
        flash("Asistencia registrada exitosamente.", "success")
        return redirect(url_for("web_user.meeting_detail", meeting_id=participant.meeting_id))
    except ValueError as e:
        flash(str(e), "warning")
    except PermissionError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "danger")
        
    return redirect(url_for("web_user.dashboard"))
