# 04 — Contrato de API

## Convenciones

Todos los endpoints de API usan prefijo `/api/` y respuestas JSON estándar.

Autenticación:

```http
Authorization: Bearer <access_token>
```

Respuesta exitosa:

```json
{
  "success": true,
  "data": {}
}
```

Respuesta de error:

```json
{
  "success": false,
  "error": {
    "message": "Descripción",
    "code": "ERROR_CODE",
    "details": {}
  }
}
```

## Auth

### POST /api/auth/login

```json
{
  "email": "usuario@ecuamatriz.local",
  "password": "password"
}
```

Devuelve `access_token`, `refresh_token` y datos del usuario.

### GET /api/auth/me

Requiere JWT. Devuelve el usuario autenticado.

## Usuarios

### GET /api/users/search

Busca usuarios para invitaciones de reunión.

Query params:

| Parámetro | Descripción |
| --- | --- |
| `q` | Busca por nombre, correo o área. |
| `area_id` | Filtra por área. |
| `limit` | Límite de resultados; default 20. |

Reglas:

- Solo usuarios activos.
- Excluye rol `admin`.

Respuesta:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 2,
        "full_name": "Juan Pérez",
        "email": "juan@ecuamatriz.local",
        "area": {
          "id": 1,
          "name": "Producción"
        },
        "role": "usuario"
      }
    ]
  }
}
```

## Reuniones

### POST /api/meetings/check-availability

Requiere JWT.

```json
{
  "date": "2026-06-12",
  "start_time": "10:00",
  "end_time": "11:00",
  "room_id": 1,
  "participant_ids": [2, 3, 4]
}
```

Respuesta:

```json
{
  "success": true,
  "data": {
    "can_create": true,
    "hard_blocks": [],
    "warnings": [],
    "room": {
      "id": 1,
      "name": "Sala Principal",
      "available": true,
      "conflicts": [],
      "hard_blocks": [],
      "warnings": []
    },
    "participants": [
      {
        "id": 2,
        "full_name": "Usuario Demo",
        "status": "available",
        "conflicts": [],
        "message": "Disponible.",
        "hard_block": null
      }
    ],
    "suggested_slots": []
  }
}
```

Estados de participante: `available`, `busy`, `pending`, `rejected`, `creator_blocked`, `outside_work_hours`, `non_working_day`.

### POST /api/meetings

Requiere JWT. Admin recibe `403`.

```json
{
  "title": "Revisión de avances",
  "objective": "Revisar avances semanales",
  "agenda_items": [
    "Revisión de pendientes",
    "Problemas encontrados",
    "Próximos compromisos"
  ],
  "description": "Opcional",
  "date": "2026-06-12",
  "start_time": "10:00",
  "end_time": "11:00",
  "modality": "presencial",
  "room_id": 1,
  "virtual_link": null,
  "participant_ids": [2, 3, 4]
}
```

Respuesta `201`:

```json
{
  "success": true,
  "data": {
    "meeting": {
      "id": 1,
      "title": "Revisión de avances",
      "status": "scheduled",
      "participants": []
    },
    "availability": {}
  },
  "message": "Recurso creado exitosamente."
}
```

Si hay bloqueos duros: `409 AVAILABILITY_BLOCKED`.

### GET /api/meetings

Requiere JWT.

Filtros:

- `date_from`
- `date_to`
- `status`
- `created_by_me=true`
- `invited=true`
- `pending_response=true`

Usuario ve reuniones creadas por él o donde fue invitado. Secretaría tiene vista amplia. Admin recibe `403`.

### GET /api/meetings/<id>

Requiere JWT. Puede ver el creador, invitado o Secretaría. Admin y usuarios ajenos reciben `403`.

### POST /api/meetings/<id>/accept

Requiere JWT. Solo participante invitado. Bloquea si el usuario ya tiene reunión creada o aceptada en ese horario.

Respuesta:

```json
{
  "success": true,
  "data": {
    "meeting_id": 1,
    "invitation_status": "accepted"
  }
}
```

### POST /api/meetings/<id>/reject

Requiere JWT. Solo participante invitado.

```json
{
  "comment": "No podré asistir por cruce de agenda"
}
```

Respuesta:

```json
{
  "success": true,
  "data": {
    "meeting_id": 1,
    "invitation_status": "rejected"
  }
}
```

### POST /api/meetings/<id>/cancel

Requiere JWT. Solo creador o Secretaría. Admin no opera reuniones.

```json
{
  "reason": "Cambio de agenda"
}
```

Marca la reunión como `cancelled`, notifica invitados y deja de bloquear disponibilidad.

### POST /api/meetings/<id>/attendance-token

Requiere JWT. Solo creador o Secretaría. Admin recibe `403`.

Genera el token QR fijo de asistencia si no existe uno activo. Si ya existe, mantiene un solo token activo y devuelve metadatos, pero no reconstruye el token plano porque solo se guarda `token_hash`.

Respuesta al crear token:

```json
{
  "success": true,
  "data": {
    "meeting_id": 1,
    "attendance_url": "http://localhost:5000/attendance/qr/<token>",
    "qr_payload": "http://localhost:5000/attendance/qr/<token>",
    "token_available": true,
    "token_created": true,
    "valid_from": "2026-06-12T09:50:00",
    "valid_until": "2026-06-12T11:20:00"
  }
}
```

Respuesta cuando ya existe token activo:

```json
{
  "success": true,
  "data": {
    "meeting_id": 1,
    "attendance_url": null,
    "qr_payload": null,
    "token_available": false,
    "token_created": false,
    "valid_from": "2026-06-12T09:50:00",
    "valid_until": "2026-06-12T11:20:00"
  }
}
```

### GET /api/meetings/<id>/attendance

Requiere JWT. Solo creador o Secretaría.

```json
{
  "success": true,
  "data": {
    "meeting_id": 1,
    "summary": {
      "total_invited": 5,
      "present": 3,
      "absent": 1,
      "not_marked": 1,
      "justified": 0
    },
    "participants": [
      {
        "user_id": 2,
        "full_name": "Usuario Demo",
        "invitation_status": "accepted",
        "attendance_status": "present",
        "attendance_method": "qr",
        "attendance_marked_at": "2026-06-12T10:05:00+00:00",
        "attendance_marked_by_user_id": 2,
        "attendance_comment": null
      }
    ]
  }
}
```

### POST /api/meetings/<id>/attendance/manual

Requiere JWT. Secretaría puede marcar si `allow_manual_attendance_by_secretary=true`. El creador puede marcar si `allow_manual_attendance_by_creator=true`. Admin no opera asistencia.

```json
{
  "user_id": 2,
  "attendance_status": "present",
  "comment": "Marcado manual por Secretaría"
}
```

Reglas:

- El usuario debe ser participante.
- Reuniones canceladas no permiten marcado.
- Usuarios que rechazaron solo pueden ser marcados por Secretaría con comentario obligatorio.
- Método registrado: `manual_secretary` o `manual_creator`.

## Asistencia QR

### POST /api/attendance/qr/<token>

Requiere JWT. Marca asistencia del usuario autenticado con QR fijo.

Reglas:

- `qr_attendance_enabled=true`.
- Token activo y válido por hash.
- Reunión no cancelada.
- Usuario participante.
- Invitación `accepted`.
- Dentro de ventana `start_time - qr_valid_before_minutes` y `end_time + qr_valid_after_minutes`.
- Doble marcado devuelve `409`.

Respuesta:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "message": "Asistencia registrada correctamente",
    "meeting_id": 1,
    "attendance_status": "present",
    "attendance_method": "qr"
  }
}
```

## Notificaciones

### GET /api/notifications/

Lista notificaciones del usuario autenticado.

### POST /api/notifications/<id>/read

Marca una notificación propia como leída.

## Códigos relevantes de Fase 2

| Código | Descripción |
| --- | --- |
| `AVAILABILITY_BLOCKED` | No se puede crear por bloqueos de disponibilidad. |
| `VALIDATION_ERROR` | Payload inválido por Marshmallow. |
| `FORBIDDEN` | Rol o usuario sin permiso. |
| `MEETING_NOT_FOUND` | Reunión inexistente. |
| `MEETING_ACCEPT_ERROR` | No se pudo aceptar la invitación. |
| `MEETING_REJECT_ERROR` | No se pudo rechazar la invitación. |
| `MEETING_CANCEL_ERROR` | No se pudo cancelar la reunión. |
| `NOTIFICATION_NOT_FOUND` | Notificación inexistente o ajena. |
| `ATTENDANCE_TOKEN_ERROR` | Error al generar u obtener token QR. |
| `QR_ATTENDANCE_ERROR` | Error al marcar asistencia por QR. |
| `MANUAL_ATTENDANCE_ERROR` | Error al marcar asistencia manual. |

## Fuera de alcance en Fase 3

Fichas técnicas, grabación, transcripción, Android, reportes Excel, FCM, WebSocket, QR dinámico/rotativo y frontend avanzado no se implementan en esta fase.

---

*Documento actualizado en Fase 3 — Agenda Ecuamatriz*
