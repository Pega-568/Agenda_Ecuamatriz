# 06 — Pantallas Web

## Estructura de plantillas

```
web/templates/
  base/
    layout_admin.html       — Layout base para Administrador
    layout_secretary.html   — Layout base para Secretaría
    layout_user.html        — Layout base para Usuario
    layout_auth.html        — Layout base para pantallas de login
  auth/
    login.html
  shared/
    navbar.html             — Barra superior con notificaciones
    sidebar_admin.html
    sidebar_secretary.html
    sidebar_user.html
    notification_center.html
    404.html
    500.html
  user/
    dashboard.html
    meeting_new.html        — Nueva reunión (flujo único)
    meeting_list.html       — Mis reuniones
    meeting_detail.html     — Detalle de reunión
    invitations.html        — Invitaciones pendientes
    qr_view.html            — Mostrar QR (si es creador)
    qr_scan.html            — Escanear QR (si es invitado) — v web
    technical_sheet.html    — Completar ficha técnica
    notifications.html      — Centro de notificaciones
    profile.html            — Perfil de usuario
  secretary/
    dashboard.html
    meetings_registry.html  — Registro de todas las reuniones
    meeting_detail.html     — Detalle con asistencia y ficha
    technical_sheets.html   — Gestión de fichas técnicas
    calendar.html           — Calendario institucional
    non_working_days.html   — Feriados y días no laborables
    institutional_events.html
    reports.html            — Exportar Excel
    audit_logs.html         — Logs funcionales
    notifications.html
  admin/
    dashboard.html
    users.html
    user_form.html
    areas.html
    rooms.html
    work_schedule.html      — Horarios laborables
    system_limits.html      — Límites del sistema
    qr_settings.html        — Configuración QR
    notification_settings.html
    audit_logs.html
```

---

## Pantallas por rol

### Pantallas de Autenticación (sin rol)

| Pantalla | URL          | Descripción                |
|----------|--------------|----------------------------|
| Login    | `/auth/login`| Formulario email/contraseña|

---

### Pantallas de Usuario

| Pantalla             | URL                            | Descripción                                    |
|----------------------|--------------------------------|------------------------------------------------|
| Dashboard            | `/user/`                       | Reuniones próximas, invitaciones pendientes    |
| Nueva reunión        | `/user/meetings/new`           | Flujo completo de creación                     |
| Mis reuniones        | `/user/meetings/`              | Lista de reuniones creadas/aceptadas           |
| Detalle reunión      | `/user/meetings/<id>`          | Info completa, estado de participantes         |
| Invitaciones         | `/user/invitations/`           | Lista con aceptar/rechazar                     |
| QR reunión           | `/user/meetings/<id>/qr`       | Mostrar QR (solo si es creador)                |
| Ficha técnica        | `/user/meetings/<id>/sheet`    | Completar/editar ficha técnica                 |
| Notificaciones       | `/user/notifications/`         | Centro de notificaciones                       |
| Perfil               | `/user/profile/`               | Editar datos personales                        |

---

### Pantallas de Secretaría

| Pantalla               | URL                              | Descripción                               |
|------------------------|----------------------------------|-------------------------------------------|
| Dashboard              | `/secretary/`                    | Resumen de reuniones del día/semana       |
| Registro reuniones     | `/secretary/meetings/`           | Todas las reuniones del sistema           |
| Detalle reunión        | `/secretary/meetings/<id>`       | Asistencia, fichas, invitados             |
| Fichas técnicas        | `/secretary/sheets/`             | Lista y gestión de fichas                 |
| Calendario             | `/secretary/calendar/`           | Vista calendario institucional            |
| Días no laborables     | `/secretary/calendar/non-working`| CRUD feriados y días no laborables        |
| Eventos institucionales| `/secretary/calendar/events`     | CRUD eventos institucionales              |
| Reportes               | `/secretary/reports/`            | Exportar Excel                            |
| Logs                   | `/secretary/logs/`               | Logs funcionales de reuniones             |
| Notificaciones         | `/secretary/notifications/`      | Centro de notificaciones                  |

---

### Pantallas de Administrador

| Pantalla               | URL                          | Descripción                               |
|------------------------|------------------------------|-------------------------------------------|
| Dashboard              | `/admin/`                    | Resumen del sistema                       |
| Usuarios               | `/admin/users/`              | CRUD usuarios                             |
| Áreas                  | `/admin/areas/`              | CRUD áreas organizacionales               |
| Salas                  | `/admin/rooms/`              | CRUD salas de reunión                     |
| Horario laboral        | `/admin/work-schedule/`      | Configurar horarios y días laborables     |
| Límites del sistema    | `/admin/limits/`             | Máx. participantes, duración, anticipación|
| Configuración QR       | `/admin/qr-settings/`        | Ventana de validez QR                     |
| Configuración notif.   | `/admin/notification-settings/`| Parámetros de notificación              |
| Logs de auditoría      | `/admin/audit/`              | Todos los logs del sistema                |

---

## Componentes compartidos

### Navbar superior (todas las vistas autenticadas)
- Logo Ecuamatriz (izquierda)
- Título del módulo actual (centro)
- Campana de notificaciones con badge de no leídas
- Nombre y foto del usuario + menú desplegable (perfil, cerrar sesión)

### Centro de notificaciones (campana)
- Panel lateral deslizable
- Lista de notificaciones (leídas / no leídas)
- Acción directa desde cada notificación (ver reunión, responder, etc.)
- Botón "marcar todas como leídas"

### Sidebar (navegación por rol)
- Fondo: `#003091` (Electric Blue)
- Ítem activo: resaltado con `#0057FF`
- Íconos + texto
- Colapasable en móvil

---

## Notas de implementación

- Las plantillas web no son pantallas independientes con estado global.
  Consumen la API del backend (misma que Android).
- No duplicar lógica de negocio en las vistas.
- Validación básica en frontend (JS) + validación completa en backend.
- Mensajes de error provenientes del backend, no inventados en el frontend.
- Responsive mínimo: tablet (768px) y desktop (1024px+).

---

*Pantallas web — Fase 0 — Agenda Ecuamatriz*
