# 02 — Flujo de Nueva Reunión

## Descripción general

Existe un **único flujo** para crear una reunión. No hay tipos de reunión, no hay caminos alternativos por jerarquía o área. Todo usuario autenticado con rol `user` puede iniciar el flujo.

---

## Diagrama del flujo completo

```
[Usuario]
    │
    ├─→ 1. DATOS GENERALES
    │       - Título (obligatorio)
    │       - Objetivo (obligatorio)
    │       - Descripción (opcional)
    │
    ├─→ 2. ORDEN DEL DÍA (obligatorio)
    │       - Lista de puntos estructurada
    │       - Mínimo 1 punto
    │       - Servirá para ficha técnica y transcripción futura
    │
    ├─→ 3. FECHA / HORA / MODALIDAD
    │       - Fecha (obligatorio)
    │       - Hora inicio (obligatorio)
    │       - Hora fin (obligatorio)
    │       - Modalidad: presencial | virtual | híbrida
    │       - Sala (obligatorio si presencial/híbrida)
    │       - Link virtual (obligatorio si virtual/híbrida)
    │
    ├─→ 4. BÚSQUEDA DE PARTICIPANTES
    │       - Buscar por nombre o área
    │       - Seleccionar múltiples participantes
    │       - Mínimo 1 participante (además del creador)
    │
    ├─→ 5. DISPONIBILIDAD INTEGRADA (no es pantalla separada)
    │       El sistema muestra en tiempo real:
    │       ✅ disponible
    │       🔴 ocupado (confirmado en otra reunión)
    │       🟡 pendiente (invitado en otra reunión sin responder)
    │       🟠 conflicto parcial
    │       ⛔ fuera de horario laboral
    │       ⛔ día no laborable
    │       🔴 sala ocupada
    │
    ├─→ 6. VALIDACIONES DEL SISTEMA
    │
    │   BLOQUEOS DUROS (no se puede crear):
    │       ✗ Fecha en feriado bloqueante
    │       ✗ Día no laborable bloqueante
    │       ✗ Fuera de horario laboral (si Admin lo bloqueó)
    │       ✗ Sala ocupada en ese horario
    │       ✗ Hora fin ≤ hora inicio
    │       ✗ Duración excede máximo configurado
    │       ✗ Más participantes que el máximo configurado
    │       ✗ Fecha demasiado próxima (< horas mínimas de anticipación)
    │
    │   ADVERTENCIAS (se puede crear con confirmación):
    │       ⚠ Participante ocupado
    │       ⚠ Participante con invitación pendiente en otra reunión
    │       ⚠ Muchos invitados con conflicto
    │
    ├─→ 7. CONFIRMACIÓN
    │       - Resumen de la reunión a crear
    │       - Lista de participantes con estado de disponibilidad
    │       - Botón confirmar / editar
    │
    ├─→ 8. CREACIÓN
    │       - Se crea la reunión en BD (status: scheduled)
    │       - Se bloquea la agenda del CREADOR automáticamente
    │       - Para invitados: queda como invitación pendiente (no bloquea agenda)
    │       - Se genera token QR
    │
    └─→ 9. INVITACIONES
            - Se envía notificación a cada participante:
              tipo: invitation_received
            - Cada invitado puede:
              → Aceptar → bloquea su agenda → notifica al creador
              → Rechazar → no bloquea → notifica al creador con comentario

─────────────────────────────────────────────────────

POST-REUNIÓN:
    ├─→ 10. QR DISPONIBLE
    │       - Notificación qr_available a participantes aceptados
    │       - Ventana de validez configurable (X min antes / Y min después)
    │
    ├─→ 11. ASISTENCIA
    │       - Invitado escanea QR → asistencia marcada como "present"
    │       - Si no escanea → queda "not_marked" hasta cierre de reunión
    │       - Secretaría/creador puede marcar manual si config lo permite
    │
    └─→ 12. FICHA TÉCNICA
            - Notificación al creador: ficha técnica pendiente
            - Datos autocargados: título, objetivo, fecha, hora, sala,
              creador, invitados, asistentes QR, ausentes, orden del día
            - Creador edita: temas tratados, resumen ejecutivo,
              acuerdos, compromisos, observaciones
            - Secretaría puede ver y finalizar
```

---

## Estados de la reunión

| Estado        | Descripción                                      |
|---------------|--------------------------------------------------|
| `scheduled`   | Reunión creada y activa                          |
| `completed`   | Reunión ya ocurrió (marcado automático o manual) |
| `cancelled`   | Cancelada por el creador                         |
| `rescheduled` | Reprogramada (genera nueva reunión vinculada)    |

---

## Estados de invitación (por participante)

| Estado     | Descripción                        | Bloquea agenda del invitado |
|------------|------------------------------------|-----------------------------|
| `pending`  | No ha respondido aún               | ❌ No                        |
| `accepted` | Aceptó la invitación               | ✅ Sí                        |
| `rejected` | Rechazó la invitación              | ❌ No                        |

---

## Estados de asistencia (por participante)

| Estado        | Descripción                         |
|---------------|-------------------------------------|
| `not_marked`  | Sin marcar                          |
| `present`     | Asistió (marcado por QR o manual)   |
| `absent`      | No asistió                          |
| `justified`   | Ausencia justificada                |

> **Importante**: invitación ≠ asistencia. Se llevan separadas.
> Un invitado puede aceptar y luego no asistir.
> Un invitado puede rechazar y aparecer como ausente en el registro.

---

## API del flujo

| Paso                          | Endpoint                               | Método |
|-------------------------------|----------------------------------------|--------|
| Verificar disponibilidad      | `/api/availability/check`             | POST   |
| Crear reunión                 | `/api/meetings/`                      | POST   |
| Ver invitaciones pendientes   | `/api/meetings/invitations`           | GET    |
| Responder invitación          | `/api/meetings/<id>/respond`          | POST   |
| Obtener QR                    | `/api/attendance/<id>/qr`             | GET    |
| Escanear QR (marcar asistencia) | `/api/attendance/scan`              | POST   |
| Ver reporte de asistencia     | `/api/attendance/<id>/report`         | GET    |
| Crear ficha técnica           | `/api/technical-sheets/<id>`          | POST   |

---

*Documento de flujo de nueva reunión — Fase 0 — Agenda Ecuamatriz*
