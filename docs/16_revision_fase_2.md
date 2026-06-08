# 16 — Revisión Fase 2

## Resultado general

Fase 2 implementa backend para reuniones, disponibilidad integrada, invitaciones, aceptación, rechazo, cancelación, notificaciones internas y auditoría. No se implementaron funcionalidades de QR, asistencia, fichas técnicas, audio, transcripción, Android ni frontend avanzado.

## Docker y PostgreSQL

- `docker compose ps`: OK.
- Servicio `agenda_ecuamatriz_db`: `healthy`.
- Puerto PostgreSQL: `5432`.
- Tests ejecutados contra `agenda_ecuamatriz_test` mediante `postgresql+psycopg://...`.
- No se usa SQLite.

## DateTime y zona horaria

Se actualizó el uso de `db.DateTime` a `db.DateTime(timezone=True)` en modelos con timestamps de sistema y auditoría.

Decisión:

- Timestamps internos de sistema usan valores timezone-aware, normalmente generados con `datetime.now(timezone.utc)`.
- Fecha y hora de reuniones se mantienen como campos separados `date`, `start_time` y `end_time`.
- Las reglas de disponibilidad comparan fecha/hora local de negocio contra horario laboral, calendario y settings.

Migración creada:

- `backend/migrations/versions/b231a19c6a0b_timezone_aware_datetimes_phase_2.py`

Validación:

- `flask db upgrade`: OK en `agenda_ecuamatriz`.

## Endpoints implementados

- `GET /api/users/search`
- `POST /api/meetings/check-availability`
- `POST /api/meetings`
- `GET /api/meetings`
- `GET /api/meetings/<id>`
- `POST /api/meetings/<id>/accept`
- `POST /api/meetings/<id>/reject`
- `POST /api/meetings/<id>/cancel`
- `GET /api/notifications/`
- `POST /api/notifications/<id>/read`

## Reglas de disponibilidad

La disponibilidad valida:

- Rango horario válido.
- Duración máxima desde settings.
- Anticipación mínima desde settings.
- Horario laboral desde `WorkSchedule`.
- Días no laborables desde `WorkCalendarDay`.
- Eventos institucionales bloqueantes.
- Sala activa y libre.
- Participantes activos.
- Exclusión de admin como participante.
- Límite de participantes desde settings.
- Conflictos del creador.
- Conflictos de invitados aceptados, pendientes o rechazados.

## Bloqueos duros

- Sala ocupada.
- Sala inactiva.
- Día no laborable bloqueante.
- Fuera de horario laboral si settings lo bloquea.
- Duración máxima excedida.
- Anticipación mínima incumplida.
- Límite de participantes excedido.
- Usuario inactivo.
- Admin invitado.
- Hora inválida.
- Creador ocupado.
- Evento institucional bloqueante.

## Advertencias

- Participante ocupado.
- Participante con invitación pendiente.
- Participante con invitación rechazada se informa como `rejected`, sin bloquear.
- Capacidad de sala superada se reporta como advertencia.

## Aceptación, rechazo y cancelación

- Invitación `pending` no bloquea agenda.
- Invitación `accepted` bloquea agenda del invitado.
- Invitación `rejected` no bloquea agenda.
- Reunión `cancelled` no bloquea disponibilidad.
- Aceptar se bloquea si el invitado ya tiene una reunión creada o aceptada en el mismo horario.
- Rechazar permite guardar comentario.
- Cancelar está permitido solo para creador o Secretaría.
- Admin no opera reuniones.

## Notificaciones y auditoría

Eventos de notificación:

- `meeting_invitation`
- `meeting_accepted`
- `meeting_rejected`
- `meeting_cancelled`

Eventos de auditoría:

- `meeting_created`
- `meeting_accepted`
- `meeting_rejected`
- `meeting_cancelled`

## Validaciones ejecutadas

- `docker compose ps`: OK, PostgreSQL healthy.
- `flask db upgrade`: OK.
- `python scripts/seed_all.py`: OK.
- `python scripts/seed_all.py`: OK, idempotente.
- `pytest`: `37 passed`.
- `python run.py` + `GET http://127.0.0.1:5000/health`: OK, HTTP 200.

Respuesta observada en logs para `/health`:

```text
"GET /health HTTP/1.1" 200 -
```

## Higiene

Confirmaciones:

- PostgreSQL Docker usado.
- No SQLite.
- Sin errores de importación.
- No se agregó `.env` real.
- No se copiaron archivos HTML o ZIP de Stitch.
- No se agregaron bases de datos, APKs ni `dist/build`.
- No se implementó QR.
- No se implementó asistencia.
- No se implementaron fichas técnicas.
- No se implementó audio/transcripción.
- No se implementó Android.

## Riesgos y pendientes

- `suggested_slots` queda como lista vacía; sugerencias inteligentes quedan para una fase posterior.
- La capacidad de sala se maneja como advertencia, no bloqueo. Si el negocio requiere bloqueo, debe cambiarse por setting o regla explícita.
- Faltan endpoints de contador de no leídas y marcado masivo de notificaciones.
- Faltan pantallas web de consumo; Fase 2 priorizó backend y tests.

---

*Revisión de Fase 2 — Agenda Ecuamatriz*
