"""
app/calendar/routes.py — Rutas del módulo Calendar
Agenda Ecuamatriz

Endpoints:
    GET    /api/calendar/days                 — Listar días del calendario
    POST   /api/calendar/days                 — Registrar día no laborable (Secretaría)
    DELETE /api/calendar/days/<id>            — Eliminar día (Secretaría)

    GET    /api/calendar/events               — Listar eventos institucionales
    POST   /api/calendar/events               — Crear evento institucional (Secretaría)
    GET    /api/calendar/events/<id>          — Detalle de evento
    PUT    /api/calendar/events/<id>          — Editar evento (Secretaría)
    DELETE /api/calendar/events/<id>          — Eliminar evento (Secretaría)

    GET    /api/calendar/validate             — Validar si fecha es laborable (autenticado)

Fase de implementación: Fase 1 (base), Fase 5 (completo)
"""

from flask import Blueprint, request

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/days", methods=["GET"])
def list_calendar_days():
    """Lista horarios laborales por día."""
    from app.calendar.service import WorkScheduleService
    from app.shared.responses import success_response

    if not WorkScheduleService.list_schedules():
        WorkScheduleService.seed_defaults()
    return success_response(data=[WorkScheduleService.to_dict(s) for s in WorkScheduleService.list_schedules()])


@calendar_bp.route("/days", methods=["POST"])
def create_calendar_day():
    """TODO (Fase 5): Registrar día no laborable/feriado. Solo Secretaría."""
    from app.shared.responses import error_response
    return error_response("Módulo calendar — implementación pendiente (Fase 5).", 501)


@calendar_bp.route("/days/<int:day_id>", methods=["DELETE"])
def delete_calendar_day(day_id):
    """TODO (Fase 5): Eliminar día no laborable. Solo Secretaría."""
    from app.shared.responses import error_response
    return error_response("Módulo calendar — implementación pendiente (Fase 5).", 501)


@calendar_bp.route("/events", methods=["GET"])
def list_institutional_events():
    """TODO (Fase 5): Listar eventos institucionales."""
    from app.shared.responses import error_response
    return error_response("Módulo calendar — implementación pendiente (Fase 5).", 501)


@calendar_bp.route("/events", methods=["POST"])
def create_institutional_event():
    """TODO (Fase 5): Crear evento institucional. Solo Secretaría."""
    from app.shared.responses import error_response
    return error_response("Módulo calendar — implementación pendiente (Fase 5).", 501)


@calendar_bp.route("/events/<int:event_id>", methods=["GET"])
def get_institutional_event(event_id):
    """TODO (Fase 5): Detalle de evento institucional."""
    from app.shared.responses import error_response
    return error_response("Módulo calendar — implementación pendiente (Fase 5).", 501)


@calendar_bp.route("/events/<int:event_id>", methods=["PUT"])
def update_institutional_event(event_id):
    """TODO (Fase 5): Editar evento institucional. Solo Secretaría."""
    from app.shared.responses import error_response
    return error_response("Módulo calendar — implementación pendiente (Fase 5).", 501)


@calendar_bp.route("/events/<int:event_id>", methods=["DELETE"])
def delete_institutional_event(event_id):
    """TODO (Fase 5): Eliminar evento institucional. Solo Secretaría."""
    from app.shared.responses import error_response
    return error_response("Módulo calendar — implementación pendiente (Fase 5).", 501)


@calendar_bp.route("/validate", methods=["GET"])
def validate_date():
    """Verifica si un weekday es laborable."""
    from app.calendar.models import WorkSchedule
    from app.calendar.service import WorkScheduleService
    from app.shared.responses import error_response, success_response

    weekday = request.args.get("weekday", type=int)
    if not weekday:
        return error_response("weekday es obligatorio.", 422, "WEEKDAY_REQUIRED")
    schedule = WorkSchedule.query.filter_by(weekday=weekday).first()
    if not schedule:
        WorkScheduleService.seed_defaults()
        schedule = WorkSchedule.query.filter_by(weekday=weekday).first()
    return success_response(data=WorkScheduleService.to_dict(schedule))


@calendar_bp.route("/work-schedules", methods=["GET"])
def list_work_schedules():
    """Lista horarios laborales."""
    return list_calendar_days()


@calendar_bp.route("/work-schedules/<int:weekday>", methods=["PUT"])
def update_work_schedule(weekday):
    """Actualiza horario laboral por día."""
    from marshmallow import ValidationError
    from app.calendar.schemas import WorkScheduleSchema
    from app.calendar.service import WorkScheduleService
    from app.shared.responses import error_response, success_response, validation_error_response

    try:
        payload = WorkScheduleSchema().load(request.get_json(silent=True) or {})
        schedule = WorkScheduleService.update_schedule(weekday, payload)
        return success_response(data=WorkScheduleService.to_dict(schedule))
    except ValidationError as exc:
        return validation_error_response(exc.messages)
    except ValueError as exc:
        return error_response(str(exc), 422, "WORK_SCHEDULE_VALIDATION_ERROR")
