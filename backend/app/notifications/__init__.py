"""
app/notifications/__init__.py
Módulo de notificaciones web y móviles.

Canales:
- Web: campana superior + centro de notificaciones (leída/no leída).
- Android: Push notifications via Firebase Cloud Messaging (FCM).

Eventos que generan notificación:
- invitation_received: Invitación a reunión recibida.
- invitation_accepted: Invitado aceptó reunión (al creador).
- invitation_rejected: Invitado rechazó reunión (al creador).
- meeting_cancelled: Reunión cancelada (a todos los participantes).
- meeting_rescheduled: Reunión reprogramada.
- meeting_reminder: Recordatorio antes de la reunión.
- qr_available: QR de asistencia disponible.
- technical_sheet_pending: Ficha técnica pendiente de completar.
- institutional_event_created: Nuevo evento institucional.
- non_working_day_added: Día no laborable registrado.

Entidad: Notification
Fase de implementación: Fase 2 (base), Fase 5 (completo), Fase 7 (FCM Android)
"""
