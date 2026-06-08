# 08 — Notificaciones

## Alcance Fase 3

Fase 3 mantiene notificaciones internas persistidas en base de datos y agrega eventos relacionados con QR/asistencia. No implementa FCM, WebSocket, Server-Sent Events ni push Android. La lectura queda disponible por API para polling futuro.

## Eventos implementados

| Tipo | Receptor | Cuándo se crea |
| --- | --- | --- |
| `meeting_invitation` | Invitado | Al crear una reunión. |
| `meeting_accepted` | Creador | Cuando un invitado acepta. |
| `meeting_rejected` | Creador | Cuando un invitado rechaza. |
| `meeting_cancelled` | Invitados | Cuando creador o Secretaría cancela. |
| `qr_available` | Creador | Cuando se crea un token QR de asistencia. |
| `attendance_marked` | Creador | Cuando un invitado marca asistencia por QR. |
| `manual_attendance_marked` | Participante | Cuando Secretaría o creador actualiza asistencia manualmente. |

## Estructura

```json
{
  "id": 1,
  "user_id": 5,
  "type": "meeting_invitation",
  "title": "Invitación a reunión",
  "message": "Has sido invitado a: Revisión de avances",
  "related_entity_type": "Meeting",
  "related_entity_id": 42,
  "is_read": false,
  "created_at": "2026-06-08T16:00:00+00:00",
  "read_at": null
}
```

## Endpoints implementados

| Endpoint | Método | Descripción |
| --- | --- | --- |
| `/api/notifications/` | GET | Lista notificaciones del usuario autenticado. |
| `/api/notifications/<id>/read` | POST | Marca una notificación propia como leída. |

## Reglas

- Las notificaciones se crean dentro de la misma transacción de la acción crítica de reunión.
- Si la reunión no se crea por bloqueos duros, no se generan notificaciones.
- Cancelar una reunión notifica a todos los invitados registrados.
- Aceptar o rechazar notifica al creador.
- Crear token QR registra `qr_available`.
- Marcar por QR registra `attendance_marked`.
- Marcar manualmente registra `manual_attendance_marked`.
- Admin no opera reuniones ni asistencia, por lo tanto no genera eventos de Fase 3.

## Pendiente

- Contador de no leídas.
- Marcar todas como leídas.
- FCM para Android.
- WebSocket o SSE si se requiere tiempo real.
- Recordatorios de reunión.

---

*Documento actualizado en Fase 3 — Agenda Ecuamatriz*
