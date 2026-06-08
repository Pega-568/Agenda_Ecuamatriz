"""
app/availability/routes.py — Rutas del módulo Availability
Agenda Ecuamatriz

NOTA: Este módulo no tiene pantalla propia.
La disponibilidad se consulta siempre dentro del flujo de nueva reunión.

Endpoints:
    POST /api/availability/check     — Verificar disponibilidad de personas y sala

Body esperado:
    {
        "date": "2024-03-15",
        "start_time": "09:00",
        "end_time": "10:00",
        "room_id": 1,
        "user_ids": [2, 3, 4]
    }

Response incluye estado por persona y sala:
    - available
    - busy (confirmado)
    - pending (pendiente de aceptar otra reunión)
    - partial_conflict
    - out_of_hours
    - non_working_day
    - room_occupied

Fase de implementación: Fase 2
"""

from flask import Blueprint

availability_bp = Blueprint("availability", __name__)


@availability_bp.route("/check", methods=["POST"])
def check_availability():
    """TODO (Fase 2): Verificar disponibilidad integrada al flujo de nueva reunión."""
    from app.shared.responses import error_response
    return error_response("Módulo availability — implementación pendiente (Fase 2).", 501)
