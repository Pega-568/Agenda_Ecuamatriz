# 17 — Revisión Fase 3

## Resultado general

Fase 3 implementa QR fijo por reunión y control de asistencia en backend. Incluye token seguro, validación por QR, consulta de asistencia, marcado manual según settings, notificaciones internas y auditoría.

No se implementaron fichas técnicas, audio/transcripción, Android, reportes Excel, QR dinámico/rotativo, escáner ni frontend avanzado.

## Migración

Migración creada:

- `backend/migrations/versions/6b7a85062386_qr_attendance_phase_3.py`

Cambios principales:

- `attendance_tokens.token` se reemplaza por `attendance_tokens.token_hash`.
- Se agregan `is_active`, `expires_at`, `created_by_user_id`, `revoked_at`.
- Se agregan `meeting_participants.attendance_marked_by_user_id` y `attendance_comment`.

La migración convierte tokens planos existentes a SHA-256 para no romper upgrades con datos previos. Los tokens nuevos usan SHA-256 desde el servicio.

## Decisión QR

- QR fijo por reunión.
- No QR rotativo en Fase 3.
- No se genera imagen QR.
- El backend devuelve `attendance_url` y `qr_payload` solo cuando crea el token.
- Se guarda únicamente `token_hash`, no token plano.

Limitación:

- Si ya existe token activo, el endpoint devuelve `attendance_url=null` porque el token plano no se puede reconstruir. Esto preserva seguridad de base de datos. El cliente debe conservar el payload cuando se crea.

## Settings

Settings creados o confirmados:

- `qr_attendance_enabled = true`
- `qr_valid_before_minutes = 10`
- `qr_valid_after_minutes = 20`
- `allow_manual_attendance_by_secretary = true`
- `allow_manual_attendance_by_creator = false`
- `require_login_for_qr_attendance = true`

El seeder migra valores legacy `15/30` de Fase 2 a `10/20` solo si coinciden con esos defaults antiguos.

## Endpoints Implementados

- `POST /api/meetings/<meeting_id>/attendance-token`
- `POST /api/attendance/qr/<token>`
- `GET /api/meetings/<meeting_id>/attendance`
- `POST /api/meetings/<meeting_id>/attendance/manual`

## Permisos

- Creador puede generar/ver token QR y consultar asistencia.
- Secretaría puede generar/ver token QR, consultar asistencia y marcar manualmente si setting lo permite.
- Creador puede marcar manualmente solo si `allow_manual_attendance_by_creator=true`.
- Admin no opera QR ni asistencia.
- Usuarios ajenos no operan ni consultan asistencia completa.

## Reglas QR

- QR debe estar habilitado.
- Token debe existir y estar activo.
- Reunión debe existir y no estar cancelada.
- Usuario debe estar autenticado.
- Usuario debe ser participante.
- Invitación debe estar `accepted`.
- Invitaciones `pending` y `rejected` no marcan por QR.
- Debe estar dentro de ventana de validez.
- Doble marcado devuelve error controlado `409`.

## Marcado Manual

- Secretaría puede marcar si setting habilitado.
- Creador puede marcar si setting habilitado.
- Reuniones canceladas no permiten marcado.
- Usuario debe ser participante.
- Usuarios rechazados solo pueden marcarse por Secretaría con comentario obligatorio.
- Se registra `attendance_marked_by_user_id`, método y comentario.

## Auditoría

Eventos registrados:

- `attendance_token_created`
- `attendance_marked_qr`
- `attendance_marked_manual`

## Notificaciones

Eventos agregados:

- `qr_available`
- `attendance_marked`
- `manual_attendance_marked`

No se implementó FCM ni WebSocket.

## Validaciones Ejecutadas

- `docker compose ps`: OK, PostgreSQL healthy.
- `flask db upgrade`: OK.
- `python scripts/seed_all.py`: OK.
- `python scripts/seed_all.py`: OK, idempotente.
- `pytest`: `46 passed`.
- `python run.py` + `GET http://127.0.0.1:5000/health`: OK, HTTP 200.

Nota de ejecución:

- No se deben correr suites pytest en paralelo contra la misma `agenda_ecuamatriz_test` porque los fixtures recrean esquema con `drop_all/create_all`.

## Higiene

Confirmaciones:

- PostgreSQL Docker usado.
- No SQLite.
- Sin errores de importación.
- No se agregó `.env` real.
- No se copiaron archivos de Stitch.
- No se agregaron DBs, APKs ni `dist/build`.
- No se implementaron fichas técnicas.
- No se implementó audio/transcripción.
- No se implementó Android.
- No se implementaron reportes Excel.

## Pendientes Para Fase 4

- Fichas técnicas/actas posteriores a reunión.
- Cálculo formal de ausentes después de ventana QR.
- UI simple para mostrar QR si se decide.
- Escáner web/Android en fases posteriores.
- QR dinámico/rotativo solo si aparece una necesidad real.

---

*Revisión de Fase 3 — Agenda Ecuamatriz*
