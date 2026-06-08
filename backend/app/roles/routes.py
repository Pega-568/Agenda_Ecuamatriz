"""
app/roles/routes.py — Rutas del módulo Roles
Agenda Ecuamatriz

Endpoints:
    GET /api/roles/   — Listar roles disponibles (Admin)

Roles del sistema:
    - admin:     Administrador técnico-operativo.
    - secretary: Secretaría institucional.
    - user:      Colaborador interno.

Fase de implementación: Fase 1
"""

from flask import Blueprint

roles_bp = Blueprint("roles", __name__)


@roles_bp.route("/", methods=["GET"])
def list_roles():
    """TODO (Fase 1): Listar roles. Solo Admin."""
    from app.shared.responses import error_response
    return error_response("Módulo roles — implementación pendiente (Fase 1).", 501)
