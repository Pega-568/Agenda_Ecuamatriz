# 14 — Revisión y Cierre de Fase 0

## Estado general

**Fase 0: APROBADA PARA INICIAR FASE 1** — las validaciones de cierre fueron ejecutadas y el bloqueo ORM de pytest quedó corregido.

Esta revisión documenta las decisiones técnicas definitivas tomadas antes de iniciar Fase 1,
corrigiendo o ajustando decisiones preliminares que hubieran generado deuda técnica.

---

## Decisiones definitivas

### 1. Autenticación — Dos canales separados

| Canal         | Mecanismo        | Blueprint           | Prefijo URL  | Usado por          |
|---------------|------------------|---------------------|--------------|--------------------|
| Web (Jinja2)  | Flask-Login      | `auth_web_bp`       | `/auth/`     | Navegador, sesiones|
| API móvil     | JWT (Flask-JWT)  | `auth_api_bp`       | `/api/auth/` | Android (Fase 7+)  |

**Reglas que NO se deben romper jamás:**
- La web Jinja2 usa sesiones de servidor con cookies seguras (Flask-Login). **Nunca JWT**.
- La API JWT existe para la app Android. **Nunca guardar JWT en localStorage web**.
- Los dos blueprints están en archivos separados (`session_routes.py` y `api_routes.py`).
- Comparten la lógica de `AuthService.authenticate()` para no duplicar código.

**Modelo User:**
- Implementa `flask_login.UserMixin`.
- La columna `is_active` hace override a `UserMixin.is_active`.
- `get_id()` retorna `str(self.id)`.
- El `user_loader` en `app/__init__.py` carga el usuario desde la BD.

**Por qué no JWT para la web:**
- Las sesiones servidor son más seguras para aplicaciones web tradicionales.
- No exponen el token en el cliente (localStorage es vulnerable a XSS).
- Flask-Login maneja expiración, sesiones permanentes y "remember me" de forma nativa.
- El contexto de uso es una intranet corporativa con acceso desde navegador.

---

### 2. Base de datos — PostgreSQL desde el inicio

**Decisión:** PostgreSQL en Docker desde el primer día, incluyendo tests.

**No usar SQLite nunca:**

| Razón                        | Impacto en el sistema                                      |
|------------------------------|-------------------------------------------------------------|
| Tipos de datos                | PostgreSQL tiene `Time`, `Date`, `JSON`, `BigInteger` nativos |
| Constraints                   | `UniqueConstraint`, `ForeignKey ON DELETE` difieren         |
| Transacciones                 | PostgreSQL tiene MVCC real; SQLite tiene bloqueos de archivo|
| Funciones de fecha             | `NOW()`, `EXTRACT()`, `INTERVAL` tienen comportamiento distinto|
| Disponibilidad (regla crítica) | Los cálculos de horario/sala/conflicto requieren semántica real |
| Reportes                       | Las queries de reporte pueden diferir entre motores         |

**Configuración:**
```
DB desarrollo: postgresql+psycopg://agenda_user:agenda_password@127.0.0.1:5432/agenda_ecuamatriz
DB test:       postgresql+psycopg://agenda_user:agenda_password@127.0.0.1:5432/agenda_ecuamatriz_test
```

**Docker:**
- `docker-compose.yml` con `postgres:16-alpine`
- Healthcheck incluido
- `docker/postgres/init.sql` crea automáticamente la BD de test al iniciar el contenedor

**Driver:** `psycopg[binary]` (v3), no `psycopg2-binary` (v2).

---

### 3. Migraciones

- Herramienta oficial: **Flask-Migrate + Alembic**
- `db.create_all()` solo se usa en tests (sobre la BD de test)
- La BD de desarrollo y producción usa siempre `flask db upgrade`

**Flujo de trabajo:**
```bash
# 1. Crear primera migración (Fase 1)
flask db init          # Solo una vez
flask db migrate -m "initial schema - all models"

# 2. Revisar el archivo en migrations/versions/ antes de aplicar

# 3. Aplicar
flask db upgrade

# 4. Revertir si hay error
flask db downgrade

# Cada cambio de modelo → nueva migración
flask db migrate -m "add column X to table Y"
flask db upgrade
```

---

### 4. Seeders

**Seeder:** `backend/scripts/seed_all.py`
- Idempotente
- Orden correcto: roles → áreas → salas → usuarios → settings
- Usuarios demo:

| Email                        | Rol       | Contraseña demo |
|------------------------------|-----------|-----------------|
| admin@ecuamatriz.local       | admin     | Admin2024!      |
| secretaria@ecuamatriz.local  | secretary | Secre2024!      |
| usuario@ecuamatriz.local     | user      | Usuario2024!    |

> ⚠️ Cambiar contraseñas demo antes de cualquier despliegue.

**Áreas:** Administración, Gerencia, Producción, Ventas, Sistemas, Talento Humano, Finanzas, Legal

**Salas:** Sala Principal (cap. 15), Sala Reuniones 1 (cap. 8), Sala Reuniones 2 (cap. 6)

---

## Riesgos mitigados

| Riesgo del proyecto anterior            | Mitigación aplicada en Fase 0                    |
|-----------------------------------------|--------------------------------------------------|
| Muchas ramas inconsistentes             | Proyecto reiniciado desde cero. Un solo repo.    |
| JWT en web → XSS vulnerability          | Web usa Flask-Login (sesiones). JWT solo Android |
| SQLite ocultaba errores PostgreSQL      | Tests sobre PostgreSQL real desde el inicio      |
| Lógica de negocio en rutas              | `service.py` obligatorio por módulo              |
| Tipos de reunión que fragmentaron flujo | Un solo flujo definido en docs/02                |
| Secretaría como cuello de botella       | Secretaría no aprueba reuniones                  |
| Admin con capacidad de crear reuniones  | Admin está prohibido de crear/participar         |
| Módulo de audio sin código externo      | Módulo stub preparado, implementación en Fase 8  |
| Pantalla de disponibilidad separada     | Disponibilidad integrada en flujo nueva reunión  |
| Endpoints paralelos web/móvil           | Un solo contrato API bajo /api/ compartido       |

---

## Qué está listo para Fase 1

| Componente                   | Estado        |
|------------------------------|---------------|
| Estructura de carpetas        | ✅ Lista       |
| Application Factory          | ✅ Lista       |
| Flask-Login integrado        | ✅ Listo       |
| Flask-JWT integrado          | ✅ Listo       |
| Flask-WTF/CSRF integrado     | ✅ Listo       |
| Modelos SQLAlchemy           | ✅ Listos      |
| Blueprints registrados       | ✅ Listos (stubs)|
| /health endpoint             | ✅ Listo       |
| requirements.txt             | ✅ Actualizado |
| .env.example                 | ✅ Actualizado |
| docker-compose.yml           | ✅ Creado      |
| docker/postgres/init.sql     | ✅ Creado      |
| conftest.py (PostgreSQL)     | ✅ Actualizado |
| test_health.py               | ✅ Actualizado |
| seed_all.py                  | ✅ Actualizado |
| pytest.ini                   | ✅ Creado      |
| Documentación (00-14)        | ✅ Completa    |

---

## Qué NO se debe implementar en Fase 1

- ❌ Ninguna pantalla web (Fase 3)
- ❌ Módulo de reuniones (Fase 2)
- ❌ Disponibilidad (Fase 2)
- ❌ QR de asistencia (Fase 4)
- ❌ Fichas técnicas (Fase 5)
- ❌ Reportes Excel (Fase 5)
- ❌ Secretaría (Fase 5)
- ❌ App Android (Fase 7)
- ❌ Audio/transcripción (Fase 8)
- ❌ Nuevos tipos de reunión (NUNCA)
- ❌ Admin creando reuniones (NUNCA)
- ❌ Secretaría como aprobación (NUNCA)

---

## Checklist para aprobar Fase 0

### Estructura
- [x] Árbol de carpetas correcto
- [x] Todos los módulos tienen `__init__.py`, `routes.py`, `models.py`
- [x] `auth` separado en `session_routes.py` y `api_routes.py`
- [x] `shared/responses.py` y `shared/decorators.py` creados

### Configuración
- [x] `.env.example` completo con todas las variables
- [x] `requirements.txt` actualizado (psycopg v3, Flask-Login, Flask-WTF)
- [x] `docker-compose.yml` creado
- [x] `docker/postgres/init.sql` creado
- [x] `.gitignore` actualizado

### Backend
- [x] `app/__init__.py` con Flask-Login, CSRF, JWT, /health
- [x] `User` model con `UserMixin`
- [x] `seed_all.py` actualizado (3 usuarios, áreas correctas, settings)
- [x] `pytest.ini` creado

### Tests
- [x] `conftest.py` usa PostgreSQL (falla si detecta SQLite)
- [x] `test_health.py` verifica /health, auth_web_bp, auth_api_bp

### Documentación
- [x] docs/00 a docs/14 creados y actualizados
- [x] docs/13_bitacora_avances.md actualizado

### Pendiente de verificación manual
- [x] `docker compose up -d` levanta PostgreSQL sin errores
- [x] `pip install -r requirements.txt` instala sin conflictos
- [ ] `flask db init` + `flask db migrate` + `flask db upgrade` exitosos (Fase 1)
- [ ] `python scripts/seed_all.py` inserta datos sin errores
- [x] `pytest` pasa (con Docker corriendo)
- [x] `GET /health` retorna `{"status": "ok"}`

---

## Auditoría de cierre ejecutada — 2026-06-08

Validación ejecutada en `D:\Agenda_Ecuamatriz`, sin implementar funcionalidades de Fase 1.

| Validación | Resultado real |
|------------|----------------|
| Docker | OK. `docker info` responde con Docker Desktop / Server 29.4.3. |
| `docker compose up -d` | OK. Crea red, volumen y contenedor `agenda_ecuamatriz_db`. |
| `docker compose ps` | OK. `agenda_ecuamatriz_db` está `Up` y `healthy`, puerto `5432`. |
| PostgreSQL | OK. Imagen `postgres:16-alpine`, PostgreSQL 16.14. |
| DB principal | OK. `SELECT 1` en `agenda_ecuamatriz` retorna `1`. |
| DB test | OK. `SELECT 1` en `agenda_ecuamatriz_test` retorna `1`. |
| Entorno Python | OK. `pip install -r requirements.txt` completó; `pip check` reporta `No broken requirements found`. |
| Flask `python run.py` | OK con variables temporales de auditoría apuntando a PostgreSQL Docker. No se creó `.env` real. |
| `/health` | OK. Responde `{"app":"Agenda Ecuamatriz","database":"ok","status":"ok"}`. |
| `pytest` | ERROR. Recolecta 6 tests, pero todos fallan en setup por `sqlalchemy.exc.InvalidRequestError`: `Meeting.created_by_user_id` no puede resolver `Meeting` al inicializar `Mapper[User(users)]`. |

### Confirmaciones de auditoría

- `pytest` fue ejecutado con `TEST_DATABASE_URL=postgresql+psycopg://agenda_user:agenda_password@127.0.0.1:5432/agenda_ecuamatriz_test`, usando PostgreSQL Docker.
- No usa SQLite: `conftest.py` falla explícitamente si `TEST_DATABASE_URL` contiene `sqlite`; la única referencia activa a SQLite es esa guarda defensiva.
- Sí hay error de importación/configuración ORM pendiente: SQLAlchemy no resuelve `Meeting` desde la relación declarada en `User`.
- No se detectó `.env` real en la raíz; solo existe `.env.example`.
- No se detectaron secretos reales en archivos fuente; las coincidencias son placeholders, nombres de variables, credenciales locales Docker de desarrollo y secretos de test marcados como no producción.
- Hay dos ZIPs de Stitch en la raíz: `stitch_agenda_ecuamatriz.zip` y `stitch_agenda_ecuamatriz_app.zip`. Esto impide confirmar "no hay archivos de Stitch copiados" como OK.
- El directorio actual no es un repositorio Git (`git rev-parse --show-toplevel` falla), por lo que no se puede confirmar el estado de archivos versionados en Git desde esta carpeta.
- En filesystem existen `backend/venv/` y `__pycache__/` generados por instalación/tests; `.gitignore` los excluye, pero al no haber repo Git no se puede auditar si están versionados.

### Pendientes antes de aprobar Fase 0

Pendientes cerrados en la estabilización final del 2026-06-08. Ver sección siguiente.

---

## Estabilización final — 2026-06-08

Se inicializó el repositorio Git local, se conectó el remoto `https://github.com/Pega-568/Agenda_Ecuamatriz.git` y se creó la rama de trabajo `phase-0/bootstrap`.

### Corrección aplicada al error ORM

- Se agregó `_register_models()` en `backend/app/__init__.py` para importar todos los modelos antes de inicializar Flask-Migrate, ejecutar `db.create_all()` en tests o configurar mappers SQLAlchemy.
- Se corrigió `AuditLog.metadata`, nombre reservado por SQLAlchemy Declarative, usando el atributo Python `metadata_json` y conservando la columna real como `"metadata"`.
- No se implementó lógica de reuniones ni funcionalidades de Fase 1.

### Modelos registrados

Se confirmó el registro de 16 tablas SQLAlchemy:
`areas`, `attendance_tokens`, `audit_logs`, `institutional_events`, `meeting_participants`, `meeting_recordings`, `meeting_transcripts`, `meetings`, `notifications`, `roles`, `rooms`, `system_settings`, `technical_sheet_drafts`, `technical_sheets`, `users`, `work_calendar_days`.

### Resultado final de validaciones

| Validación | Resultado final |
|------------|-----------------|
| Docker / PostgreSQL | OK. `agenda_ecuamatriz_db` está `healthy`. |
| DB principal | OK. `SELECT 1` en `agenda_ecuamatriz` retorna `1`. |
| DB test | OK. `SELECT 1` en `agenda_ecuamatriz_test` retorna `1`. |
| `pytest` | OK. 6 tests recolectados, 6 passed, 2 warnings de deprecación por `datetime.utcnow()`. |
| `/health` | OK. Responde `{"app":"Agenda Ecuamatriz","database":"ok","status":"ok"}`. |
| SQLite | No usado. `pytest` se ejecutó con PostgreSQL Docker mediante `TEST_DATABASE_URL`. |
| `.env` real | No existe en la raíz. |
| Secretos | No se detectaron secretos reales en archivos fuente. |
| Stitch ZIP/HTML | `stitch_*.zip` y `*.html` quedan ignorados por Git. |
| Archivos generados | `venv/`, `__pycache__/`, `.pytest_cache/`, `node_modules/`, `dist/`, `build/`, APK y DB quedan ignorados. |

### Estado de cierre

Fase 0 queda aprobada técnicamente para iniciar Fase 1. Las tareas de migración inicial, seeder y CRUD base siguen perteneciendo a Fase 1 y no fueron ejecutadas como implementación funcional durante este cierre.

---

## Siguiente paso — Inicio de Fase 1

1. Levantar Docker: `docker compose up -d`
2. Crear entorno virtual e instalar dependencias
3. Copiar `.env.example` → `.env` y configurar valores reales
4. Ejecutar migración inicial: `flask db migrate -m "initial schema"` + `flask db upgrade`
5. Ejecutar seeder: `python scripts/seed_all.py`
6. Implementar `app/auth/service.py` (authenticate con bcrypt)
7. Implementar `app/auth/session_routes.py` (login/logout web)
8. Implementar `app/auth/api_routes.py` (login JWT para pruebas de API)
9. Implementar `app/users/` (CRUD + búsqueda)
10. Implementar `app/areas/`, `app/rooms/`, `app/settings/`
11. Escribir tests de cada módulo
12. Actualizar bitácora

---

*Documento de revisión de Fase 0 — Agenda Ecuamatriz*
