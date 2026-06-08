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

## Fuera de alcance en Fase 2

Los endpoints de QR, asistencia, fichas técnicas, grabación, transcripción, Android, FCM y WebSocket no se implementan en esta fase.

---

*Documento actualizado en Fase 2 — Agenda Ecuamatriz*
