# 02 — Flujo de Nueva Reunión

## Alcance Fase 2

Fase 2 implementa el núcleo backend para crear reuniones, verificar disponibilidad integrada, gestionar invitaciones y aceptar, rechazar o cancelar reuniones. No implementa QR, asistencia, fichas técnicas, audio, transcripción, Android ni pantallas avanzadas.

## Flujo implementado

```
[Usuario o Secretaría autenticado]
    |
    +--> 1. Busca participantes
    |       GET /api/users/search
    |       - Busca por nombre, correo o área.
    |       - Solo devuelve usuarios activos.
    |       - Excluye rol admin.
    |
    +--> 2. Valida disponibilidad integrada
    |       POST /api/meetings/check-availability
    |       - Fecha y horas.
    |       - Sala.
    |       - Participantes.
    |       - Reglas de horario laboral, calendario y settings.
    |
    +--> 3. Crea reunión
    |       POST /api/meetings
    |       - Creador bloquea agenda desde la creación.
    |       - Invitados quedan en invitation_status=pending.
    |       - Pendientes no bloquean agenda.
    |       - Se generan notificaciones y auditoría.
    |
    +--> 4. Invitado responde
            POST /api/meetings/<id>/accept
            POST /api/meetings/<id>/reject
            - accepted bloquea agenda del invitado.
            - rejected no bloquea agenda.
            - aceptar se bloquea si hay conflicto confirmado.
```

## Roles

| Rol | Crear | Listar/ver | Responder invitación | Cancelar |
| --- | --- | --- | --- | --- |
| `admin` | No | No | No | No |
| `secretaria` | Sí | Vista amplia | Sí, si fue invitada | Sí |
| `usuario` | Sí | Creadas o invitado | Sí, si fue invitado | Solo creador |

## Bloqueos duros

- Hora fin menor o igual a hora inicio.
- Duración mayor que `max_meeting_duration_minutes`.
- Anticipación menor que `min_meeting_notice_minutes`.
- Más participantes que `max_meeting_participants`.
- Sala inexistente, inactiva u ocupada.
- Día no laborable bloqueante.
- Fuera de horario laboral cuando `allow_meetings_outside_work_hours=false`.
- Evento institucional bloqueante.
- Usuario invitado inexistente, inactivo o admin.
- Creador con reunión creada o aceptada en el mismo horario.

## Advertencias

- Participante con reunión aceptada o creada en el horario.
- Participante con invitación pendiente en el horario.
- Participante con invitación rechazada se informa como `rejected`, pero no bloquea.
- Capacidad de sala superada se reporta como advertencia.

## Estados de reunión

| Estado | Descripción |
| --- | --- |
| `scheduled` | Reunión activa creada. |
| `cancelled` | Reunión cancelada; no bloquea disponibilidad. |
| `completed` | Reservado para fases posteriores. |
| `rescheduled` | Reservado para fases posteriores. |

## Estados de invitación

| Estado | Bloquea agenda del invitado | Descripción |
| --- | --- | --- |
| `pending` | No | Invitado sin respuesta. |
| `accepted` | Sí | Invitado aceptó la reunión. |
| `rejected` | No | Invitado rechazó la reunión. |

## Pendiente para fases posteriores

- QR y asistencia.
- Fichas técnicas.
- Grabación, transcripción y resumen automático.
- Android y FCM.
- Sugerencias inteligentes de horarios. En Fase 2 `suggested_slots` queda como lista vacía documentada.

---

*Documento actualizado en Fase 2 — Agenda Ecuamatriz*
