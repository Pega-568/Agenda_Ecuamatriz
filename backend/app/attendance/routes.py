"""
app/attendance/routes.py — Rutas del módulo Attendance / QR
Agenda Ecuamatriz

Endpoints:
    GET    /api/attendance/<meeting_id>/qr       — Obtener QR de la reunión (creador)
    POST   /api/attendance/scan                  — Marcar asistencia escaneando QR
    GET    /api/attendance/<meeting_id>/report   — Ver asistencia de reunión
    PUT    /api/attendance/<meeting_id>/manual   — Marcar asistencia manual (Secretaría/creador)

Fase de implementación: Fase 4
"""

from flask import Blueprint

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/<int:meeting_id>/qr", methods=["GET"])
def get_meeting_qr(meeting_id):
    """TODO (Fase 4): Obtener QR fijo de reunión. Solo creador."""
    from app.shared.responses import error_response
    return error_response("Módulo attendance — implementación pendiente (Fase 4).", 501)


@attendance_bp.route("/scan", methods=["POST"])
def scan_qr():
    """TODO (Fase 4): Marcar asistencia mediante escaneo QR."""
    from app.shared.responses import error_response
    return error_response("Módulo attendance — implementación pendiente (Fase 4).", 501)


@attendance_bp.route("/<int:meeting_id>/report", methods=["GET"])
def get_attendance_report(meeting_id):
    """TODO (Fase 4): Ver reporte de asistencia de una reunión."""
    from app.shared.responses import error_response
    return error_response("Módulo attendance — implementación pendiente (Fase 4).", 501)


@attendance_bp.route("/<int:meeting_id>/manual", methods=["PUT"])
def manual_attendance(meeting_id):
    """TODO (Fase 5): Marcar asistencia manual. Secretaría o creador."""
    from app.shared.responses import error_response
    return error_response("Módulo attendance — implementación pendiente (Fase 5).", 501)
