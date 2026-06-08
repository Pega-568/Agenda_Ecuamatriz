# 10 — Ficha Técnica y Módulo de Audio

## Parte 1: Ficha Técnica (Manual/Asistida) — Fase 5

### Descripción

La ficha técnica es el acta de la reunión. Se genera después de que la reunión ocurre.

**Primera versión**: Manual/asistida. Los datos base se autocompletan; el creador edita el contenido.

---

### Datos autocargados desde la reunión

| Campo              | Fuente                              |
|--------------------|-------------------------------------|
| Título             | `Meeting.title`                     |
| Objetivo           | `Meeting.objective`                 |
| Fecha              | `Meeting.date`                      |
| Hora inicio        | `Meeting.start_time`                |
| Hora fin           | `Meeting.end_time`                  |
| Sala               | `Room.name`                         |
| Creador            | `User.full_name` (created_by)       |
| Lista de invitados | `MeetingParticipant` (todos)        |
| Asistentes QR      | `MeetingParticipant.attendance_status = present` |
| Ausentes           | `MeetingParticipant.attendance_status = absent/not_marked` |
| Orden del día      | `Meeting.agenda_items`              |

---

### Campos editables

| Campo               | Descripción                                      |
|---------------------|--------------------------------------------------|
| `topics_discussed`  | Temas efectivamente discutidos                   |
| `executive_summary` | Síntesis ejecutiva de la reunión                 |
| `agreements`        | Acuerdos tomados en la reunión                   |
| `commitments`       | Compromisos con responsables y fechas            |
| `observations`      | Notas adicionales y aclaraciones                 |

---

### Estados de la ficha

| Estado      | Descripción                                   |
|-------------|-----------------------------------------------|
| `draft`     | En edición. Se puede modificar.               |
| `finalized` | Cerrada. Solo lectura. No se puede modificar. |

---

### Quién puede editar

- El **creador** de la reunión puede crear y editar la ficha mientras está en `draft`.
- **Secretaría** puede ver todas las fichas y finalizarlas.
- Los **participantes** pueden ver la ficha (solo lectura).

---

## Parte 2: Módulo de Audio y Transcripción — Fase 8

> ⚠️ **MÓDULO FUTURO**
> No implementar hasta recibir el código del compañero responsable de grabación/transcripción.
> La arquitectura está preparada para recibirlo sin romper el sistema existente.

---

### Arquitectura preparada

```
MeetingRecording          — Registro de grabación
    ↓
MeetingTranscript         — Texto transcrito por proveedor externo
    ↓
TechnicalSheetDraft       — Borrador generado desde la transcripción
    ↓ (revisión humana obligatoria)
TechnicalSheet            — Ficha técnica final
```

---

### Reglas del módulo futuro

1. **La transcripción genera BORRADOR, no ficha final automática.**
2. **Siempre requiere revisión humana** antes de finalizar.
3. El borrador se muestra al creador para edición.
4. El creador aprueba o corrige el borrador.
5. El borrador aprobado se convierte en `TechnicalSheet`.

---

### Proveedores de transcripción (planificados)

| Proveedor        | Estado     |
|------------------|------------|
| OpenAI Whisper   | Planificado|
| Google Speech    | Planificado|
| Proveedor custom | Pendiente (código externo) |

La abstracción `TranscriptionProvider` permite cambiar de proveedor sin afectar el resto del sistema.

---

### Pantalla Android de grabación (Fase 8)

- Solo disponible para el **creador** de la reunión.
- Botón "Iniciar grabación" en detalle de reunión (durante la reunión).
- Muestra tiempo transcurrido y estado de grabación.
- Botón "Detener grabación" → envía al backend.
- Notificación cuando la transcripción esté lista.

---

### Qué NO se hace en Fase 8

- No se modifica el flujo de reuniones existente.
- No se obliga a grabar para completar ficha técnica.
- La ficha técnica manual sigue funcionando independientemente.
- No se almacena audio sin consentimiento implícito (el creador inicia la grabación).

---

*Documento de ficha técnica y audio — Fase 0 — Agenda Ecuamatriz*
