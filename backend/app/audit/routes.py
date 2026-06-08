"""
app/audit/routes.py — Rutas del módulo Audit
Agenda Ecuamatriz

Endpoints:
    GET /api/audit/   — Listar logs de auditoría (Admin/Secretaría, paginado)

Fase de implementación: Fase 1 (estructura), Fase 6 (interfaz completa Admin)
"""

from flask import Blueprint

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/", methods=["GET"])
def list_audit_logs():
    """TODO (Fase 6): Listar logs de auditoría del sistema."""
    from app.shared.responses import error_response
    return error_response("Módulo audit — implementación pendiente (Fase 6).", 501)
