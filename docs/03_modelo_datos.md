# 03 — Modelo de Datos

## Entidades del sistema

### Diagrama de relaciones (simplificado)

```
Role ──< User >── Area
              │
              ├──< Meeting (como creador)
              ├──< MeetingParticipant
              ├──< Notification
              └──< AuditLog (como actor)

Meeting ──< MeetingParticipant
        ├── Room
        ├── AttendanceToken
        ├── TechnicalSheet
        ├── MeetingRecording (Fase 8)
        └── MeetingTranscript (Fase 8)

SystemSetting (tabla key-value)
WorkCalendarDay
InstitutionalEvent
```

---

## Entidades detalladas

### User

| Campo              | Tipo         | Requerido | Descripción                              |
|--------------------|--------------|-----------|------------------------------------------|
| id                 | Integer PK   | ✅        |                                          |
| first_name         | String(100)  | ✅        |                                          |
| last_name          | String(100)  | ✅        |                                          |
| email              | String(255)  | ✅        | Único, indexado                          |
| phone              | String(30)   | ❌        |                                          |
| position           | String(150)  | ❌        | Cargo en la empresa                      |
| password_hash      | String(255)  | ✅        |                                          |
| role_id            | FK Role      | ✅        |                                          |
| area_id            | FK Area      | ❌        |                                          |
| fcm_token          | String(512)  | ❌        | Token FCM para notificaciones Android    |
| is_active          | Boolean      | ✅        | Default: True                            |
| created_at         | DateTime     | ✅        |                                          |
| updated_at         | DateTime     | ✅        |                                          |
| last_login_at      | DateTime     | ❌        |                                          |

---

### Role

| Campo       | Tipo        | Requerido | Descripción              |
|-------------|-------------|-----------|--------------------------|
| id          | Integer PK  | ✅        |                          |
| name        | String(100) | ✅        | Nombre legible           |
| slug        | String(50)  | ✅        | admin / secretary / user |
| description | Text        | ❌        |                          |

---

### Area

| Campo       | Tipo        | Requerido |
|-------------|-------------|-----------|
| id          | Integer PK  | ✅        |
| name        | String(150) | ✅ único  |
| description | Text        | ❌        |
| is_active   | Boolean     | ✅        |
| created_at  | DateTime    | ✅        |
| updated_at  | DateTime    | ✅        |

---

### Room

| Campo                | Tipo        | Requerido |
|----------------------|-------------|-----------|
| id                   | Integer PK  | ✅        |
| name                 | String(150) | ✅ único  |
| location             | String(255) | ❌        |
| capacity             | Integer     | ✅        |
| description          | Text        | ❌        |
| has_projector        | Boolean     | ✅        |
| has_video_conference | Boolean     | ✅        |
| is_active            | Boolean     | ✅        |
| created_at           | DateTime    | ✅        |
| updated_at           | DateTime    | ✅        |

---

### SystemSetting

Patrón key-value. Un registro por parámetro.

| Campo               | Tipo       | Requerido | Descripción                   |
|---------------------|------------|-----------|-------------------------------|
| id                  | Integer PK | ✅        |                               |
| key                 | String(100)| ✅ único  |                               |
| value               | Text       | ✅        |                               |
| data_type           | String(20) | ✅        | string / int / bool / json    |
| description         | Text       | ❌        |                               |
| updated_at          | DateTime   | ✅        |                               |
| updated_by_user_id  | FK User    | ❌        |                               |

---

### WorkCalendarDay

| Campo               | Tipo       | Requerido | Descripción                        |
|---------------------|------------|-----------|------------------------------------|
| id                  | Integer PK | ✅        |                                    |
| date                | Date       | ✅ único  | Indexado                           |
| is_working_day      | Boolean    | ✅        |                                    |
| blocks_meetings     | Boolean    | ✅        | True = bloqueo duro                |
| label               | String(150)| ❌        | Ej: "Feriado Nacional"             |
| reason              | Text       | ❌        |                                    |
| created_by_user_id  | FK User    | ❌        |                                    |
| created_at          | DateTime   | ✅        |                                    |

---

### InstitutionalEvent

| Campo               | Tipo        | Requerido |
|---------------------|-------------|-----------|
| id                  | Integer PK  | ✅        |
| title               | String(255) | ✅        |
| description         | Text        | ❌        |
| date                | Date        | ✅        |
| start_time          | Time        | ❌        |
| end_time            | Time        | ❌        |
| blocks_agenda       | Boolean     | ✅        |
| created_by_user_id  | FK User     | ✅        |
| created_at          | DateTime    | ✅        |
| updated_at          | DateTime    | ✅        |

---

### Meeting

| Campo                | Tipo        | Requerido | Descripción                               |
|----------------------|-------------|-----------|-------------------------------------------|
| id                   | Integer PK  | ✅        |                                           |
| title                | String(255) | ✅        |                                           |
| objective            | Text        | ✅        |                                           |
| agenda_items         | JSON        | ✅        | Lista de puntos del orden del día         |
| description          | Text        | ❌        |                                           |
| date                 | Date        | ✅        | Indexado                                  |
| start_time           | Time        | ✅        |                                           |
| end_time             | Time        | ✅        |                                           |
| modality             | String(20)  | ✅        | in_person / virtual / hybrid              |
| room_id              | FK Room     | ❌        | Requerido si modality != virtual          |
| virtual_link         | String(512) | ❌        | Requerido si modality != in_person        |
| created_by_user_id   | FK User     | ✅        |                                           |
| status               | String(20)  | ✅        | scheduled/completed/cancelled/rescheduled |
| created_at           | DateTime    | ✅        |                                           |
| updated_at           | DateTime    | ✅        |                                           |
| cancelled_at         | DateTime    | ❌        |                                           |
| cancellation_reason  | Text        | ❌        |                                           |

---

### MeetingParticipant

| Campo                    | Tipo       | Requerido | Descripción                       |
|--------------------------|------------|-----------|-----------------------------------|
| id                       | Integer PK | ✅        |                                   |
| meeting_id               | FK Meeting | ✅        | Indexado                          |
| user_id                  | FK User    | ✅        | Indexado                          |
| invitation_status        | String(20) | ✅        | pending / accepted / rejected     |
| response_comment         | Text       | ❌        |                                   |
| responded_at             | DateTime   | ❌        |                                   |
| attendance_status        | String(20) | ✅        | not_marked/present/absent/justified|
| attendance_method        | String(30) | ❌        | qr / manual_secretary / manual_creator |
| attendance_marked_at     | DateTime   | ❌        |                                   |
| attendance_justification | Text       | ❌        |                                   |

**Constraint**: `UNIQUE(meeting_id, user_id)` — Un usuario solo aparece una vez por reunión.

---

### AttendanceToken

| Campo          | Tipo        | Requerido | Descripción                       |
|----------------|-------------|-----------|-----------------------------------|
| id             | Integer PK  | ✅        |                                   |
| meeting_id     | FK Meeting  | ✅ único  | Un QR por reunión                 |
| token          | String(255) | ✅ único  | UUID codificado en el QR          |
| qr_image_path  | String(512) | ❌        | Ruta al archivo PNG del QR        |
| created_at     | DateTime    | ✅        |                                   |

---

### Notification

| Campo                | Tipo        | Requerido |
|----------------------|-------------|-----------|
| id                   | Integer PK  | ✅        |
| user_id              | FK User     | ✅        |
| type                 | String(50)  | ✅        |
| title                | String(255) | ✅        |
| message              | Text        | ✅        |
| related_entity_type  | String(50)  | ❌        |
| related_entity_id    | Integer     | ❌        |
| is_read              | Boolean     | ✅        |
| created_at           | DateTime    | ✅        |
| read_at              | DateTime    | ❌        |

---

### TechnicalSheet

| Campo               | Tipo       | Requerido |
|---------------------|------------|-----------|
| id                  | Integer PK | ✅        |
| meeting_id          | FK Meeting | ✅ único  |
| topics_discussed    | Text       | ❌        |
| executive_summary   | Text       | ❌        |
| agreements          | Text       | ❌        |
| commitments         | Text       | ❌        |
| observations        | Text       | ❌        |
| status              | String(20) | ✅        | draft / finalized |
| created_by_user_id  | FK User    | ✅        |
| created_at          | DateTime   | ✅        |
| updated_at          | DateTime   | ✅        |
| finalized_at        | DateTime   | ❌        |

---

### AuditLog

| Campo             | Tipo        | Requerido |
|-------------------|-------------|-----------|
| id                | Integer PK  | ✅        |
| actor_user_id     | FK User     | ❌        |
| action            | String(100) | ✅        |
| entity_type       | String(50)  | ❌        |
| entity_id         | Integer     | ❌        |
| metadata          | JSON        | ❌        |
| created_at        | DateTime    | ✅        |

---

### MeetingRecording (Fase 8)

| Campo               | Tipo        | Requerido |
|---------------------|-------------|-----------|
| id                  | Integer PK  | ✅        |
| meeting_id          | FK Meeting  | ✅        |
| file_path           | String(512) | ❌        |
| storage_provider    | String(50)  | ❌        |
| duration_seconds    | Integer     | ❌        |
| file_size_bytes     | BigInteger  | ❌        |
| mime_type           | String(50)  | ❌        |
| status              | String(30)  | ✅        |
| started_by_user_id  | FK User     | ❌        |
| created_at          | DateTime    | ✅        |
| completed_at        | DateTime    | ❌        |

---

### MeetingTranscript / TechnicalSheetDraft (Fase 8)

Ver `app/transcriptions/models.py` para detalle completo.

---

*Documento de modelo de datos — Fase 0 — Agenda Ecuamatriz*
