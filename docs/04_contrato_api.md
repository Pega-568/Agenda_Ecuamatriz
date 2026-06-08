# 04 — Contrato de API

## Convenciones generales

### Prefijo base
Todos los endpoints de la API llevan el prefijo `/api/`.

### Autenticación
```
Authorization: Bearer <access_token>
```
El token JWT se obtiene en `POST /api/auth/login`.

### Formato de respuesta exitosa
```json
{
  "success": true,
  "data": { ... },
  "message": "Descripción opcional"
}
```

### Formato de respuesta paginada
```json
{
  "success": true,
  "data": [ ... ],
  "meta": {
    "total": 50,
    "page": 1,
    "per_page": 20,
    "total_pages": 3
  }
}
```

### Formato de error
```json
{
  "success": false,
  "error": {
    "message": "Descripción del error",
    "code": "ERROR_CODE_OPCIONAL",
    "details": { ... }
  }
}
```

### Códigos HTTP usados

| Código | Significado                         |
|--------|-------------------------------------|
| 200    | OK                                  |
| 201    | Creado                              |
| 400    | Error en datos de entrada           |
| 401    | No autenticado                      |
| 403    | Sin permisos                        |
| 404    | Recurso no encontrado               |
| 409    | Conflicto (duplicado, estado inválido) |
| 422    | Datos de entrada inválidos (validación) |
| 500    | Error interno del servidor          |
| 501    | No implementado (módulo en desarrollo) |

---

## Módulo Auth

### POST /api/auth/login
```json
// Request
{
  "email": "usuario@ecuamatriz.com",
  "password": "contraseña"
}

// Response 200
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "user": {
      "id": 1,
      "full_name": "Juan Pérez",
      "email": "usuario@ecuamatriz.com",
      "role": "user"
    }
  }
}
```

### POST /api/auth/logout
```json
// Headers: Authorization: Bearer <token>
// Response 200
{ "success": true, "message": "Sesión cerrada." }
```

### GET /api/auth/me
```json
// Response 200
{
  "success": true,
  "data": {
    "id": 1,
    "full_name": "Juan Pérez",
    "email": "usuario@ecuamatriz.com",
    "role": "user",
    "area": "Tecnología"
  }
}
```

---

## Módulo Meetings

### POST /api/meetings/
```json
// Request
{
  "title": "Revisión de presupuesto Q3",
  "objective": "Revisar y aprobar el presupuesto del tercer trimestre",
  "agenda_items": [
    "Revisión de gastos actuales",
    "Proyección Q3",
    "Aprobación de incrementos"
  ],
  "description": "Descripción opcional",
  "date": "2024-07-15",
  "start_time": "10:00",
  "end_time": "11:30",
  "modality": "in_person",
  "room_id": 1,
  "participant_ids": [2, 3, 4]
}

// Response 201
{
  "success": true,
  "data": {
    "id": 42,
    "title": "Revisión de presupuesto Q3",
    "status": "scheduled",
    ...
  },
  "message": "Reunión creada exitosamente."
}
```

### POST /api/meetings/<id>/respond
```json
// Request
{
  "status": "accepted",  // o "rejected"
  "comment": "No puedo asistir por viaje de trabajo"
}

// Response 200
{
  "success": true,
  "message": "Respuesta registrada."
}
```

---

## Módulo Availability

### POST /api/availability/check
```json
// Request
{
  "date": "2024-07-15",
  "start_time": "10:00",
  "end_time": "11:30",
  "room_id": 1,
  "user_ids": [2, 3, 4]
}

// Response 200
{
  "success": true,
  "data": {
    "date_status": "available",  // available | non_working_day | holiday
    "room": {
      "id": 1,
      "name": "Sala Quito",
      "status": "available"  // available | occupied
    },
    "participants": [
      { "user_id": 2, "full_name": "Ana García", "status": "available" },
      { "user_id": 3, "full_name": "Pedro Ruiz", "status": "busy" },
      { "user_id": 4, "full_name": "María López", "status": "pending" }
    ],
    "blocking_issues": [],
    "warnings": [
      { "type": "participant_busy", "user_id": 3, "message": "Pedro Ruiz tiene reunión confirmada en ese horario." }
    ]
  }
}
```

---

## Módulo Attendance / QR

### GET /api/attendance/<meeting_id>/qr
```json
// Response 200
{
  "success": true,
  "data": {
    "meeting_id": 42,
    "token": "uuid-token-here",
    "qr_image_url": "/api/attendance/42/qr/image",
    "valid_from": "2024-07-15T09:45:00",
    "valid_until": "2024-07-15T12:00:00"
  }
}
```

### POST /api/attendance/scan
```json
// Request
{
  "token": "uuid-token-here"
}

// Response 200
{
  "success": true,
  "message": "Asistencia marcada correctamente.",
  "data": {
    "meeting_title": "Revisión de presupuesto Q3",
    "marked_at": "2024-07-15T10:05:00",
    "method": "qr"
  }
}

// Errores posibles:
// 403 FORBIDDEN: Usuario no es participante de esta reunión
// 409 ALREADY_MARKED: Ya marcó asistencia
// 422 QR_NOT_VALID_YET: Fuera de ventana de validez
// 422 QR_EXPIRED: Reunión ya terminó (ventana cerrada)
// 404 MEETING_NOT_FOUND
// 409 MEETING_CANCELLED
```

---

## Códigos de error internos (campo `code`)

| Código                   | Descripción                                    |
|--------------------------|------------------------------------------------|
| `VALIDATION_ERROR`       | Campos de entrada inválidos                    |
| `INVALID_TOKEN`          | JWT inválido o expirado                        |
| `USER_NOT_FOUND`         | Usuario no existe                              |
| `FORBIDDEN`              | Sin permisos para la acción                    |
| `MEETING_NOT_FOUND`      | Reunión no existe                              |
| `MEETING_CANCELLED`      | Reunión está cancelada                         |
| `ROOM_UNAVAILABLE`       | Sala ocupada en ese horario                    |
| `NON_WORKING_DAY`        | Día no laborable bloqueante                    |
| `OUTSIDE_HOURS`          | Fuera del horario laboral                      |
| `MAX_PARTICIPANTS`       | Máximo de participantes excedido               |
| `MAX_DURATION`           | Duración máxima excedida                       |
| `NOT_PARTICIPANT`        | Usuario no es participante de la reunión       |
| `ALREADY_MARKED`         | Asistencia ya fue marcada                      |
| `QR_NOT_VALID_YET`       | Fuera de ventana de validez (demasiado temprano)|
| `QR_EXPIRED`             | Fuera de ventana de validez (expirado)         |
| `SHEET_ALREADY_FINALIZED`| Ficha ya está finalizada                       |

---

*Documento de contrato API — Fase 0 — Agenda Ecuamatriz*
