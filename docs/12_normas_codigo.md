# 12 — Normas de Código

## Principios generales

1. **Un módulo = una responsabilidad.** No mezclar lógica de negocio de distintos módulos.
2. **No mezclar lógica de negocio con vistas.** Las rutas orquestan, los servicios ejecutan.
3. **No duplicar lógica entre web y API.** La web Jinja2 consume la misma API que Android.
4. **Toda acción crítica registra auditoría.**
5. **Toda regla de negocio tiene al menos un test.**
6. **No dejar código muerto.** Si algo no se usa, se elimina.
7. **No dejar TODO sin documentar.** Cada TODO indica la fase de implementación.

---

## Estructura de un módulo backend

Cada módulo en `app/` debe tener:

```
app/modulo/
  __init__.py    — Docstring con descripción y fase de implementación
  routes.py      — Blueprints + endpoints. Solo orquestación.
  models.py      — Modelos SQLAlchemy
  service.py     — Lógica de negocio (cuando se implemente en su fase)
  schemas.py     — Serializadores/validadores Marshmallow
```

Opcionalmente:
```
  repository.py  — Consultas complejas a BD
  utils.py       — Utilidades específicas del módulo
```

---

## Reglas de routes.py

```python
# ✅ Correcto: la ruta solo orquesta
@meetings_bp.route("/", methods=["POST"])
@jwt_required()
@require_role("user")
def create_meeting():
    data = request.get_json()
    errors = CreateMeetingSchema().validate(data)
    if errors:
        return validation_error_response(errors)

    meeting = MeetingService.create(data, creator_id=get_jwt_identity())
    return created_response(MeetingSchema().dump(meeting))

# ❌ Incorrecto: lógica de negocio en la ruta
@meetings_bp.route("/", methods=["POST"])
def create_meeting():
    data = request.get_json()
    # Verificar sala disponible... calcular conflictos... crear reunión...
    # ← NUNCA HACER ESTO EN ROUTES
```

---

## Reglas de service.py

- Un servicio por módulo.
- Métodos estáticos o de clase para lógica sin estado.
- Accede a la BD a través de los modelos.
- Lanza excepciones de negocio (no errores HTTP).
- Las rutas capturan excepciones y convierten a respuestas HTTP.

```python
# Excepciones de negocio personalizadas (en shared/exceptions.py)
class BusinessError(Exception):
    def __init__(self, message, code=None, status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code
```

---

## Reglas de schemas.py (Marshmallow)

- Un schema por operación principal si los campos difieren (CreateMeetingSchema, UpdateMeetingSchema).
- Validar siempre en el schema, no en la ruta ni en el servicio.
- Retornar errores de validación con `validation_error_response(errors)`.

---

## Respuestas JSON

**Siempre** usar las funciones de `app/shared/responses.py`:

```python
from app.shared.responses import (
    success_response,
    created_response,
    error_response,
    validation_error_response,
    paginated_response,
)
```

**Nunca** usar `jsonify()` directamente en una ruta.

---

## Auditoría

Registrar auditoría en toda acción crítica:

```python
from app.audit.service import AuditService

AuditService.log(
    actor_user_id=current_user_id,
    action="meeting.create",
    entity_type="Meeting",
    entity_id=meeting.id,
    metadata={"title": meeting.title, "participant_count": len(participants)},
)
```

---

## Tests

### Organización
```
tests/
  test_health.py           — Tests de sanidad del servidor
  test_auth.py             — Tests de autenticación
  test_users.py            — Tests de usuarios
  test_meetings.py         — Tests del flujo de reuniones
  test_availability.py     — Tests de disponibilidad con casos edge
  test_attendance.py       — Tests del flujo QR
  test_notifications.py
  ...
```

### Reglas de tests
- Usar `pytest` con fixtures de `conftest.py`.
- BD en memoria (SQLite) para tests. Nunca usar PostgreSQL real.
- Cada test es aislado (rollback al finalizar).
- Nombrar tests descriptivamente: `test_create_meeting_blocked_on_holiday`.
- Testear casos edge: QR expirado, sala ocupada, fuera de horario, usuario desactivado.
- Cobertura mínima de reglas de negocio: 100%.

```bash
# Ejecutar todos los tests
pytest backend/tests/ -v

# Con cobertura
pytest backend/tests/ --cov=app --cov-report=html
```

---

## Git y control de versiones

### Commits
Usar formato: `<tipo>(<módulo>): <descripción>`

| Tipo     | Uso                                           |
|----------|-----------------------------------------------|
| feat     | Nueva funcionalidad                           |
| fix      | Corrección de error                           |
| docs     | Documentación únicamente                      |
| refactor | Refactorización sin cambio de comportamiento  |
| test     | Añadir o corregir tests                       |
| chore    | Mantenimiento, dependencias, configuración    |
| migration| Nueva migración de BD                         |

Ejemplos:
```
feat(auth): implementar login con JWT
fix(meetings): corregir validación de hora fin < hora inicio
docs(readme): actualizar instrucciones de instalación
migration(users): agregar campo position a tabla users
```

### Lo que NUNCA va en un commit
- Archivos `.env`
- Contraseñas o tokens reales
- APKs
- Archivos generados (dist/, venv/, __pycache__/)
- Archivos de IDE (.idea/, .vscode/)
- Logs de la aplicación

---

## Migraciones

Cada cambio al modelo debe tener su migración:

```bash
# Generar migración automática
flask db migrate -m "descripción del cambio"

# Revisar el archivo generado en migrations/versions/ ANTES de aplicar
# Aplicar
flask db upgrade

# Revertir si hay error
flask db downgrade
```

**Nunca modificar directamente la base de datos en producción sin migración.**

---

## Variables de entorno

- Nunca leer `os.getenv()` directamente en módulos de negocio.
- La configuración se carga en `create_app()` y se accede via `current_app.config`.
- Para valores de `SystemSetting` (configuración dinámica), usar `SystemSettingService.get(key)`.

---

*Normas de código — Fase 0 — Agenda Ecuamatriz*
