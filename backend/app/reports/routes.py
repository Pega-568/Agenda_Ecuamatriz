"""
app/reports/routes.py — Rutas del módulo Reports
Agenda Ecuamatriz

Endpoints:
    GET /api/reports/meetings        — Exportar Excel de reuniones (Secretaría)
    GET /api/reports/attendance      — Exportar Excel de asistencia (Secretaría)
    GET /api/reports/technical-sheets — Exportar Excel de fichas técnicas (Secretaría)

Respuesta: archivo .xlsx descargable.
Fase de implementación: Fase 5
"""

from flask import Blueprint

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/meetings", methods=["GET"])
def export_meetings_report():
    """TODO (Fase 5): Exportar reporte de reuniones a Excel."""
    from app.shared.responses import error_response
    return error_response("Módulo reports — implementación pendiente (Fase 5).", 501)


@reports_bp.route("/attendance", methods=["GET"])
def export_attendance_report():
    """TODO (Fase 5): Exportar reporte de asistencia a Excel."""
    from app.shared.responses import error_response
    return error_response("Módulo reports — implementación pendiente (Fase 5).", 501)


@reports_bp.route("/technical-sheets", methods=["GET"])
def export_technical_sheets_report():
    """TODO (Fase 5): Exportar reporte de fichas técnicas a Excel."""
    from app.shared.responses import error_response
    return error_response("Módulo reports — implementación pendiente (Fase 5).", 501)
