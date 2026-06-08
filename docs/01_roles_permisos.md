# 01 — Roles y Permisos del Sistema

## Roles definidos

El sistema tiene **3 roles**. Los slugs son fijos y se usan en decoradores de código.

| Slug        | Nombre         | Descripción                                                        |
|-------------|----------------|--------------------------------------------------------------------|
| `admin`     | Administrador  | Rol técnico-operativo. Configura el sistema, no participa en reuniones. |
| `secretary` | Secretaría     | Gestión de registros, fichas, reportes y calendario institucional. |
| `user`      | Usuario        | Colaborador interno. Crea reuniones, acepta/rechaza, marca asistencia. |

---

## ADMINISTRADOR (`admin`)

### Qué puede hacer

| Acción                                          | Permitido |
|-------------------------------------------------|-----------|
| Gestionar usuarios (crear, editar, desactivar)  | ✅         |
| Gestionar áreas                                 | ✅         |
| Gestionar salas                                 | ✅         |
| Configurar horarios laborales                   | ✅         |
| Configurar límites del sistema                  | ✅         |
| Configurar parámetros QR                        | ✅         |
| Configurar parámetros de notificación           | ✅         |
| Ver logs de auditoría                           | ✅         |
| Ver configuración del sistema                   | ✅         |

### Qué NO puede hacer

| Acción                                | Prohibido |
|---------------------------------------|-----------|
| Crear reuniones                       | ❌         |
| Participar en reuniones               | ❌         |
| Aparecer como invitado                | ❌         |
| Marcar asistencia                     | ❌         |
| Gestionar fichas técnicas             | ❌         |
| Gestionar calendario institucional    | ❌         |
| Exportar reportes de reuniones        | ❌         |

> **Razón**: El Administrador es un rol técnico puro. No tiene presencia en los flujos de negocio de reuniones.

---

## SECRETARÍA (`secretary`)

### Qué puede hacer

| Acción                                              | Permitido |
|-----------------------------------------------------|-----------|
| Ver todas las reuniones                             | ✅         |
| Ver invitados y sus respuestas                      | ✅         |
| Ver asistencia real de cada reunión                 | ✅         |
| Gestionar fichas técnicas                           | ✅         |
| Gestionar calendario institucional                  | ✅         |
| Registrar feriados y días no laborables             | ✅         |
| Crear eventos institucionales                       | ✅         |
| Exportar reportes a Excel                           | ✅         |
| Consultar logs funcionales                          | ✅         |
| Marcar asistencia manual (si config lo permite)     | ✅         |

### Qué NO puede hacer

| Acción                             | Prohibido |
|------------------------------------|-----------|
| Gestionar usuarios                 | ❌         |
| Gestionar áreas                    | ❌         |
| Gestionar salas                    | ❌         |
| Cambiar parámetros del sistema     | ❌         |
| Aprobar reuniones (no es cuello de botella) | ❌ |

> **Regla clave**: Secretaría **no aprueba reuniones**. No es un paso obligatorio en el flujo. Secretaría gestiona el registro, no la autorización.

---

## USUARIO (`user`)

### Qué puede hacer

| Acción                                                | Permitido |
|-------------------------------------------------------|-----------|
| Crear reuniones                                       | ✅         |
| Buscar personas dentro de la empresa                  | ✅         |
| Seleccionar participantes                             | ✅         |
| Ver disponibilidad (dentro del flujo de reunión)      | ✅         |
| Seleccionar sala disponible                           | ✅         |
| Enviar invitación                                     | ✅         |
| Aceptar reuniones en las que fue invitado             | ✅         |
| Rechazar reuniones en las que fue invitado            | ✅         |
| Ver sus propias reuniones                             | ✅         |
| Ver sus invitaciones pendientes                       | ✅         |
| Marcar asistencia escaneando QR                       | ✅         |
| Mostrar QR si es creador de la reunión                | ✅         |
| Completar ficha técnica si es creador                 | ✅         |
| Iniciar grabación (Fase 8)                            | ✅ (futuro) |

### Qué NO puede hacer

| Acción                                          | Prohibido |
|-------------------------------------------------|-----------|
| Gestionar usuarios                              | ❌         |
| Gestionar áreas                                 | ❌         |
| Gestionar salas                                 | ❌         |
| Ver toda la agenda de otras personas            | ❌         |
| Ver detalles privados de reuniones ajenas       | ❌         |
| Exportar reportes globales                      | ❌         |
| Crear feriados o eventos institucionales        | ❌         |
| Cambiar parámetros del sistema                  | ❌         |

---

## Matriz de permisos por endpoint

| Endpoint                          | admin | secretary | user |
|-----------------------------------|-------|-----------|------|
| GET /api/users/                   | ✅    | ❌         | ❌   |
| POST /api/users/                  | ✅    | ❌         | ❌   |
| GET /api/areas/                   | ✅    | ✅         | ✅   |
| POST /api/areas/                  | ✅    | ❌         | ❌   |
| GET /api/rooms/                   | ✅    | ✅         | ✅   |
| POST /api/rooms/                  | ✅    | ❌         | ❌   |
| GET /api/settings/                | ✅    | ❌         | ❌   |
| PUT /api/settings/                | ✅    | ❌         | ❌   |
| GET /api/settings/public          | ✅    | ✅         | ✅   |
| POST /api/meetings/               | ❌    | ❌         | ✅   |
| GET /api/meetings/ (propias)      | ❌    | ❌         | ✅   |
| GET /api/meetings/all             | ❌    | ✅         | ❌   |
| POST /api/meetings/<id>/respond   | ❌    | ❌         | ✅   |
| GET /api/attendance/<id>/qr       | ❌    | ❌         | ✅ (creador) |
| POST /api/attendance/scan         | ❌    | ❌         | ✅   |
| PUT /api/attendance/<id>/manual   | ❌    | ✅         | ✅ (creador) |
| GET /api/calendar/days            | ✅    | ✅         | ✅   |
| POST /api/calendar/days           | ❌    | ✅         | ❌   |
| GET /api/reports/meetings         | ❌    | ✅         | ❌   |
| GET /api/audit/                   | ✅    | ✅         | ❌   |

---

## Implementación en código

Los permisos se aplican mediante el decorador `@require_role` en `app/shared/decorators.py`:

```python
@meetings_bp.route("/", methods=["POST"])
@jwt_required()
@require_role("user")
def create_meeting():
    ...

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@require_role("admin")
def list_users():
    ...

@calendar_bp.route("/days", methods=["POST"])
@jwt_required()
@require_role("secretary")
def create_calendar_day():
    ...
```

---

*Documento de roles y permisos — Fase 0 — Agenda Ecuamatriz*
