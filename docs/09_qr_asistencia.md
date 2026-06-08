# 09 — QR de Asistencia

## Decisión de diseño

**QR fijo por reunión.** No QR rotativo en la primera versión.

Razones:
- Simplicidad de implementación y depuración.
- El QR rotativo agrega complejidad sin beneficio significativo en contexto interno de empresa.
- La ventana de tiempo configurable mitiga el riesgo de uso fuera de contexto.
- El QR exige usuario autenticado, lo que ya limita el uso indebido.

---

## Generación del QR

- Se genera automáticamente al crear la reunión.
- Contiene una URL con el token UUID: `https://agenda.ecuamatriz.com/api/attendance/scan`
- El token UUID es único por reunión y se almacena en `AttendanceToken`.
- Se genera un archivo PNG del QR y se guarda en `QR_OUTPUT_DIR`.

### Biblioteca Python
```python
import qrcode
import uuid

token = str(uuid.uuid4())
qr = qrcode.make(f"{APP_URL}/api/attendance/scan?token={token}")
qr.save(f"{QR_OUTPUT_DIR}/{token}.png")
```

---

## Ventana de validez

| Parámetro                   | Config key               | Default |
|-----------------------------|--------------------------|---------|
| Minutos antes del inicio    | `qr_valid_minutes_before`| 15 min  |
| Minutos después del fin     | `qr_valid_minutes_after` | 30 min  |

```
Reunión: 10:00 - 11:30
QR válido desde: 09:45 (15 min antes)
QR válido hasta: 12:00 (30 min después)
```

---

## Validaciones al escanear

El backend valida **en orden**:

1. ✅ Token existe en `AttendanceToken`
2. ✅ La reunión asociada existe
3. ✅ La reunión no está cancelada
4. ✅ El usuario está autenticado (JWT válido)
5. ✅ El usuario es participante de esa reunión
6. ✅ El usuario está dentro de la ventana de validez (inicio - before ≤ now ≤ fin + after)
7. ✅ El usuario no ha marcado asistencia previamente

Si alguna validación falla → error con código específico.

---

## Flujo completo

```
[Usuario Android/Web]
    │
    ├─→ Abre app → escanea QR con cámara
    │
    ├─→ App extrae token del QR
    │
    ├─→ POST /api/attendance/scan
    │       { "token": "uuid-aqui" }
    │       + JWT en header
    │
    ├─→ Backend ejecuta validaciones (ver arriba)
    │
    ├─→ Si válido:
    │       - attendance_status = "present"
    │       - attendance_method = "qr"
    │       - attendance_marked_at = now()
    │       - Retorna 200 con confirmación
    │
    └─→ Si inválido:
            - Retorna error con código descriptivo
```

---

## Estados de asistencia resultantes

| Estado        | Cómo se llega                                    |
|---------------|--------------------------------------------------|
| `not_marked`  | Estado inicial (no escaneó QR)                   |
| `present`     | Escaneó QR exitosamente                          |
| `absent`      | Marcado por Secretaría/creador (ausencia)        |
| `justified`   | Ausencia registrada con justificación            |

---

## Asistencia manual

Si la configuración lo permite (`allow_manual_attendance_secretary` / `allow_manual_attendance_creator`):
- Secretaría puede marcar `present`, `absent` o `justified` para cualquier participante.
- El creador puede marcar asistencia manual para sus invitados.
- Se registra `attendance_method = "manual_secretary"` o `"manual_creator"`.

---

## Pantalla QR en web

- **Creador** de la reunión puede ver el QR desde el detalle de la reunión.
- El QR se muestra como imagen (PNG servida desde el backend).
- Se puede imprimir o proyectar para que los asistentes lo escaneen.

---

## Pantalla QR en Android

- **Escaneo**: Pantalla con cámara usando CameraX + ML Kit Barcode.
- **Mostrar QR**: Si el usuario es creador, puede mostrar el QR en su pantalla.
- La app envía el token al backend y muestra el resultado (ok / error).

---

*Documento QR de asistencia — Fase 0 — Agenda Ecuamatriz*
