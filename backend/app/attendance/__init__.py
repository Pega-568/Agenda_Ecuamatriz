"""
app/attendance/__init__.py
Módulo de asistencia y QR.

Responsabilidades:
- Generar QR fijo por reunión (no rotativo en v1).
- Validar QR al escanear.
- Marcar asistencia (qr, manual_secretary, manual_creator).
- Respetar ventana de validez configurada por Admin.

Estados de asistencia:
- not_marked: Sin marcar aún.
- present: Presente (asistió).
- absent: Ausente (no asistió).
- justified: Ausencia justificada.

Validaciones QR:
- Reunión existe y no está cancelada.
- Usuario autenticado.
- Usuario es invitado de esa reunión.
- Dentro de ventana válida (X min antes — X min después).
- No ha marcado asistencia previamente.

Entidad: AttendanceToken (QR fijo), MeetingParticipant (estado de asistencia)
Fase de implementación: Fase 4
"""
