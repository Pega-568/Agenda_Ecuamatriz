# 08 — Notificaciones

## Canales

### Web
- **Campana superior**: Muestra badge con cantidad de no leídas.
- **Centro de notificaciones**: Panel con lista completa.
- **Acción directa**: Cada notificación puede llevar a la entidad relacionada.

### Android (Fase 7)
- **Firebase Cloud Messaging (FCM)**: Notificaciones push remotas.
- Al tocar la notificación push, navegar a la pantalla correspondiente.

---

## Eventos que generan notificación

| Tipo                         | Slug                            | Receptor          | Descripción                                           |
|------------------------------|---------------------------------|-------------------|-------------------------------------------------------|
| Invitación recibida          | `invitation_received`           | Invitados         | Fuiste invitado a una reunión                         |
| Invitación aceptada          | `invitation_accepted`           | Creador           | [Nombre] aceptó tu reunión                           |
| Invitación rechazada         | `invitation_rejected`           | Creador           | [Nombre] rechazó tu reunión                          |
| Reunión cancelada            | `meeting_cancelled`             | Todos los participantes | La reunión fue cancelada                       |
| Reunión reprogramada         | `meeting_rescheduled`           | Todos los participantes | La reunión fue reprogramada                    |
| Recordatorio de reunión      | `meeting_reminder`              | Participantes aceptados | Reunión en X minutos                          |
| QR disponible                | `qr_available`                  | Participantes aceptados | El QR de asistencia ya está disponible        |
| Ficha técnica pendiente      | `technical_sheet_pending`       | Creador           | Completa la ficha técnica de tu reunión              |
| Evento institucional creado  | `institutional_event_created`   | Todos los usuarios| Nuevo evento institucional registrado                |
| Día no laborable registrado  | `non_working_day_added`         | Todos los usuarios| Se registró un nuevo día no laborable                |

---

## Estructura de notificación en BD

```json
{
  "id": 1,
  "user_id": 5,
  "type": "invitation_received",
  "title": "Invitación a reunión",
  "message": "Juan Pérez te invitó a 'Revisión de presupuesto Q3' el 15 de julio a las 10:00.",
  "related_entity_type": "Meeting",
  "related_entity_id": 42,
  "is_read": false,
  "created_at": "2024-07-10T09:30:00",
  "read_at": null
}
```

---

## Endpoints de notificaciones

| Endpoint                              | Método | Descripción                         |
|---------------------------------------|--------|-------------------------------------|
| `/api/notifications/`                 | GET    | Listar notificaciones del usuario   |
| `/api/notifications/unread-count`     | GET    | Cantidad de no leídas               |
| `/api/notifications/<id>/read`        | PUT    | Marcar una como leída               |
| `/api/notifications/read-all`         | PUT    | Marcar todas como leídas            |

---

## Servicio de notificaciones (arquitectura)

El servicio de notificaciones debe:
1. Crear el registro en la tabla `Notification`.
2. Enviar push FCM si el usuario tiene `fcm_token` registrado (Fase 7).
3. No bloquear el flujo principal si la notificación falla.
   (Error en notificación → log, no excepción)

```python
# Ejemplo de uso en servicio de reuniones
from app.notifications.service import NotificationService

NotificationService.send(
    user_id=participant.user_id,
    type=NotificationType.INVITATION_RECEIVED,
    title="Invitación a reunión",
    message=f"{creator.full_name} te invitó a '{meeting.title}'",
    related_entity_type="Meeting",
    related_entity_id=meeting.id,
)
```

---

## Parámetros configurables (Admin)

| Parámetro                         | Tipo    | Default | Descripción                        |
|-----------------------------------|---------|---------|------------------------------------|
| `notifications_reminder_minutes`  | int     | 30      | Minutos antes de la reunión para recordatorio |

---

## Notificaciones en tiempo real (futuro)

En la primera versión, las notificaciones web se cargan por polling (petición al abrir la campana o con refresh periódico).

En versiones futuras puede implementarse WebSocket o Server-Sent Events para notificaciones en tiempo real sin polling.

---

*Documento de notificaciones — Fase 0 — Agenda Ecuamatriz*
