# 09 — QR de Asistencia

## Decisión de diseño

Fase 3 implementa QR fijo por reunión. No implementa QR dinámico, rotativo ni generación de imagen PNG. El backend devuelve el payload/URL para que una fase web posterior pueda renderizar el QR.

Razones:

- Mantiene simple el primer control de asistencia.
- La ventana de validez reduce uso fuera de contexto.
- El endpoint exige usuario autenticado.
- El token plano no se persiste en base de datos.

## Token

El servicio genera un token aleatorio con `secrets.token_urlsafe(32)`.

Persistencia:

- Se guarda `token_hash` SHA-256.
- No se guarda token plano.
- La validación compara hash del token recibido contra `attendance_tokens.token_hash`.

Limitación documentada:

- Si ya existe un token activo, el endpoint mantiene un solo token activo y devuelve metadatos, pero `attendance_url` y `qr_payload` salen `null` porque el token plano no puede reconstruirse. El cliente debe conservar la URL recibida al crear el token.

## Generación

Endpoint:

```http
POST /api/meetings/<meeting_id>/attendance-token
Authorization: Bearer <access_token>
```

Permisos:

- Creador de la reunión.
- Secretaría.
- Admin no opera QR.

Reglas:

- Reunión debe existir.
- Reunión no debe estar cancelada.
- Si ya existe token activo, no se crea otro.
- Al crear token se registra auditoría `attendance_token_created`.

Respuesta al crear:

```json
{
  "meeting_id": 1,
  "attendance_url": "http://localhost:5000/attendance/qr/<token>",
  "qr_payload": "http://localhost:5000/attendance/qr/<token>",
  "token_available": true,
  "token_created": true,
  "valid_from": "2026-06-12T09:50:00",
  "valid_until": "2026-06-12T11:20:00"
}
```

## Ventana de validez

Settings:

| Config key | Default |
| --- | --- |
| `qr_attendance_enabled` | `true` |
| `qr_valid_before_minutes` | `10` |
| `qr_valid_after_minutes` | `20` |
| `require_login_for_qr_attendance` | `true` |

Ejemplo:

```text
Reunión: 10:00 - 11:00
QR válido desde: 09:50
QR válido hasta: 11:20
```

## Marcado por QR

Endpoint:

```http
POST /api/attendance/qr/<token>
Authorization: Bearer <access_token>
```

Validaciones:

1. QR habilitado por setting.
2. Token existe y está activo.
3. Reunión existe.
4. Reunión no está cancelada.
5. Usuario autenticado y activo.
6. Usuario es participante.
7. Invitación está `accepted`.
8. Fecha/hora actual está dentro de ventana QR.
9. Asistencia no fue marcada previamente.

Resultado:

- `attendance_status = present`
- `attendance_method = qr`
- `attendance_marked_at = now UTC`
- `attendance_marked_by_user_id = usuario autenticado`
- Auditoría `attendance_marked_qr`

## Consulta de asistencia

Endpoint:

```http
GET /api/meetings/<meeting_id>/attendance
```

Permisos:

- Creador.
- Secretaría.
- Admin no.
- Usuarios ajenos no.

Devuelve resumen por estado y lista de participantes con estado de invitación y asistencia.

## Marcado manual

Endpoint:

```http
POST /api/meetings/<meeting_id>/attendance/manual
```

Body:

```json
{
  "user_id": 2,
  "attendance_status": "present",
  "comment": "Marcado manual por Secretaría"
}
```

Settings:

| Config key | Default |
| --- | --- |
| `allow_manual_attendance_by_secretary` | `true` |
| `allow_manual_attendance_by_creator` | `false` |

Reglas:

- Secretaría puede marcar si el setting está habilitado.
- Creador puede marcar solo si su setting está habilitado.
- Admin no opera asistencia.
- Reunión cancelada no permite marcado.
- Usuario debe ser participante.
- Usuarios que rechazaron solo pueden ser marcados por Secretaría con comentario obligatorio.
- Método registrado: `manual_secretary` o `manual_creator`.
- Auditoría `attendance_marked_manual`.

## No Implementado En Fase 3

- QR dinámico o rotativo.
- Imagen QR base64 o PNG.
- Escáner web o Android.
- Finalización de asistencia.
- Cálculo persistido de ausentes.
- Fichas técnicas.
- Reportes Excel.

Ausentes se podrán calcular en fases posteriores como participantes `accepted` con `attendance_status = not_marked` después de la ventana QR.

---

*Documento actualizado en Fase 3 — Agenda Ecuamatriz*
