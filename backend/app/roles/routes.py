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
    """Lista roles disponibles."""
    from app.roles.service import RoleService
    from app.shared.responses import success_response

    return success_response(data=[RoleService.to_dict(role) for role in RoleService.list_roles()])
