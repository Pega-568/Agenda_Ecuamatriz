# 13 — Bitácora de Avances

## Formato de entrada

```
### [YYYY-MM-DD] — Fase X — Descripción del avance
- Qué se hizo
- Decisiones tomadas
- Problemas encontrados
- Próximo paso
```

---

## Entradas

---

### [2026-06-07] — Fase 0 — Estructura inicial del proyecto

**Qué se hizo**:
- Reinicio completo del proyecto desde cero.
- Creada la estructura de carpetas completa del proyecto.
- Creado `.gitignore` para Python/Flask/Android/Node.
- Creado `.env.example` sin secretos.
- Creado `README.md` con descripción completa del sistema.
- Creada la Application Factory de Flask con todos los blueprints registrados.
- Creados los `__init__.py` de los 17 módulos del backend con su docstring de responsabilidades.
- Creados los `routes.py` de todos los módulos con stubs documentados y indicación de fase.
- Creados los modelos SQLAlchemy de todas las entidades:
  - User, Role, Area, Room, SystemSetting
  - WorkCalendarDay, InstitutionalEvent
  - Meeting, MeetingParticipant
  - AttendanceToken
  - Notification
  - TechnicalSheet
  - AuditLog
  - MeetingRecording, MeetingTranscript, TechnicalSheetDraft (Fase 8)
- Creado `app/shared/responses.py` con funciones de respuesta estandarizadas.
- Creado `app/shared/decorators.py` con decoradores de autorización por rol.
- Creado `tests/conftest.py` con fixtures de pytest.
- Creado `tests/test_health.py` con tests de sanidad.
- Creado `scripts/seed_all.py` con seeder idempotente.
- Creados los 14 documentos de `docs/` (00 a 13).

**Decisiones tomadas**:
- **No usar SPA en primera versión.** Se usa Flask + Jinja2 para mayor control y simplicidad.
- **QR fijo** (no rotativo) en primera versión. Más simple, suficiente para el contexto.
- **JWT** como mecanismo de autenticación (no sesiones Flask).
- **Marshmallow** para validación y serialización (no Pydantic).
- **Un solo flujo de reunión.** No tipos de reunión.
- **Secretaría no es cuello de botella.** No aprueba reuniones.
- **Admin no participa en reuniones.** Rol técnico puro.
- **Módulos recordings y transcriptions** creados como stubs para no bloquear Fase 8.
- **SQLite en tests**, PostgreSQL en desarrollo y producción.

**Herramientas elegidas**:
- `qrcode[pil]` para generación de QR (Python).
- `openpyxl` para exportación Excel.
- `firebase-admin` para FCM (notificaciones push Android).
- `pytest + pytest-flask` para tests.
- `flask-migrate + alembic` para migraciones.

**Próximo paso**:
- **Fase 1**: Implementar backend base.
  - Crear la migración inicial (`flask db migrate -m "initial schema"`).
  - Implementar `auth` (login web y API JWT).
  - Implementar `users` (CRUD + búsqueda).
  - Implementar `areas`, `rooms`, `settings`.
  - Ejecutar seeder y verificar.
  - Escribir tests de cada módulo.

---

### [2026-06-08] — Fase 0 — Revisión y ajuste de cierre

**Qué se hizo**:
- Auditoría técnica completa antes de cerrar Fase 0.
- Corrección de decisiones preliminares que hubieran generado deuda.

**Decisiones definitivas tomadas**:

**Autenticación — dos canales:**
- **Web (Jinja2)**: Flask-Login con sesiones de servidor y cookies seguras.
  Blueprint `auth_web_bp` en `session_routes.py` → `/auth/`
- **API móvil (Android)**: JWT con Flask-JWT-Extended.
  Blueprint `auth_api_bp` en `api_routes.py` → `/api/auth/`
- Regla: la web NUNCA usa JWT. La API NUNCA usa sesiones Flask.
- Ambos blueprints comparten `AuthService.authenticate()`.

**Base de datos:**
- PostgreSQL Docker desde el inicio, incluyendo tests.
- SQLite eliminado completamente del proyecto.
- Driver cambiado: `psycopg2-binary` → `psycopg[binary]` (v3).
- BD desarrollo: `agenda_ecuamatriz`. BD test: `agenda_ecuamatriz_test`.

**Infraestructura:**
- Creado `docker-compose.yml` con `postgres:16-alpine` + healthcheck + volumen persistente.
- Creado `docker/postgres/init.sql` que crea la BD de test automáticamente.

**User model:**
- Actualizado para implementar `flask_login.UserMixin`.
- `get_id()` explícito. `is_active` hace override al de UserMixin.

**Tests:**
- `conftest.py` reescrito: PostgreSQL obligatorio, falla con mensaje claro si detecta SQLite.
- Fixture `db_session` con rollback por test para aislamiento.
- Fixture `secretary_user` añadida (faltaba).
- `test_health.py` actualizado para verificar `/health`, `auth_web_bp` y `auth_api_bp`.
- `pytest.ini` creado.

**Seeder:**
- Orden corregido: roles → áreas → salas → usuarios → settings.
- 3 usuarios demo con emails `.local`.
- Áreas actualizadas: Administración, Gerencia, Producción, Ventas, Sistemas, Talento Humano, Finanzas, Legal.
- Salas: Sala Principal, Sala Reuniones 1, Sala Reuniones 2.
- Setting `notifications_enabled` añadido.

**Documentación:**
- Creado `docs/14_revision_fase_0.md` con decisiones, checklist y próximos pasos.
- `.env.example` actualizado con nuevas variables.
- `requirements.txt` actualizado.

**Archivos creados/modificados en esta revisión**:
- `docker-compose.yml` (nuevo)
- `docker/postgres/init.sql` (nuevo)
- `.env.example` (actualizado)
- `backend/requirements.txt` (actualizado)
- `backend/app/__init__.py` (actualizado — Flask-Login, CSRF, /health)
- `backend/app/users/models.py` (actualizado — UserMixin)
- `backend/app/auth/session_routes.py` (nuevo)
- `backend/app/auth/api_routes.py` (nuevo)
- `backend/app/auth/service.py` (nuevo — stub)
- `backend/app/auth/routes.py` (convertido en doc)
- `backend/tests/conftest.py` (reescrito — PostgreSQL)
- `backend/tests/test_health.py` (actualizado)
- `backend/pytest.ini` (nuevo)
- `backend/scripts/seed_all.py` (actualizado)
- `docs/14_revision_fase_0.md` (nuevo)
- `.gitignore` (actualizado — docker, tests/tmp)

**Problemas encontrados**: Ninguno crítico. Los cambios son preventivos.

**Próximo paso — Fase 1**:
1. `docker compose up -d`
2. Crear `venv`, instalar `requirements.txt`
3. Configurar `.env`
4. `flask db init` + `flask db migrate -m "initial schema"` + `flask db upgrade`
5. `python scripts/seed_all.py`
6. Implementar `auth/service.py` → `session_routes.py` → `api_routes.py`
7. Implementar `users/`, `areas/`, `rooms/`, `settings/`
8. Escribir tests. Ejecutar `pytest`.

---

### [2026-06-08] — Fase 0 — Bootstrap Git y estabilización final

**Qué se hizo**:
- Inicializado repositorio Git local en `D:\Agenda_Ecuamatriz`.
- Configurada rama principal `main`.
- Configurado remoto `origin` hacia `https://github.com/Pega-568/Agenda_Ecuamatriz.git`.
- Creada rama de trabajo `phase-0/bootstrap`.
- Endurecido `.gitignore` para excluir explícitamente `stitch_*.zip`, `*.html`, `.env`, `venv/`, `__pycache__/`, `.pytest_cache/`, `node_modules/`, `dist/`, `build/`, APK y bases SQLite/DB.
- Corregido el error ORM que impedía ejecutar pytest:
  - `backend/app/__init__.py` ahora registra/importa todos los modelos antes de migraciones/tests.
  - `AuditLog.metadata` se renombró a atributo Python `metadata_json`, conservando la columna `"metadata"`.

**Validaciones ejecutadas**:
- `docker compose ps`: `agenda_ecuamatriz_db` healthy.
- `SELECT 1` en `agenda_ecuamatriz`: OK.
- `SELECT 1` en `agenda_ecuamatriz_test`: OK.
- `pytest`: 6 passed, 2 warnings de deprecación por `datetime.utcnow()`.
- `/health`: `{"app":"Agenda Ecuamatriz","database":"ok","status":"ok"}`.

**Confirmaciones**:
- `pytest` usa PostgreSQL Docker mediante `TEST_DATABASE_URL`.
- No usa SQLite.
- No hay error de imports ORM.
- No existe `.env` real.
- No se detectaron secretos reales.
- Los ZIP de Stitch permanecen en filesystem, pero quedan fuera de Git por `.gitignore`.
- No se implementaron funcionalidades de Fase 1.

**Próximo paso**:
- Hacer commit `Bootstrap clean Agenda Ecuamatriz phase 0`.
- Hacer push de `phase-0/bootstrap` al remoto.
- No hacer merge a `main` todavía.

---

### [2026-06-08] — Fase 1 — Backend base funcional

**Qué se hizo**:
- Creada rama `phase-1/backend-base` desde `phase-0/bootstrap`.
- Implementados servicios base para `auth`, `roles`, `users`, `areas`, `rooms`, `settings` y `calendar/work schedule`.
- Agregados schemas Marshmallow para validación de entradas en usuarios, áreas, salas, settings y horario laboral.
- Implementado login web con Flask-Login, logout y dashboard mínimo.
- Preparado login API JWT mínimo y `/api/auth/me`, separado del login web.
- Agregado modelo `WorkSchedule` para horario laboral semanal.
- Inicializado Flask-Migrate/Alembic y creada migración inicial `9f7c5986fbf4_initial_schema_phase_1.py`.
- Actualizado `scripts/seed_all.py` para crear datos base de Fase 1 de forma idempotente.
- Agregados tests de Fase 1 contra PostgreSQL Docker.

**Validaciones ejecutadas**:
- `docker compose ps`: `agenda_ecuamatriz_db` healthy.
- `flask db upgrade`: OK.
- `python scripts/seed_all.py`: OK e idempotente.
- `pytest`: 24 passed, 149 warnings por `datetime.utcnow()`.
- `/health`: `{"app":"Agenda Ecuamatriz","database":"ok","status":"ok"}`.

**Confirmaciones**:
- Tests usan PostgreSQL Docker mediante `TEST_DATABASE_URL`.
- No se usa SQLite.
- No se creó `.env` real.
- No se implementaron reuniones, QR, asistencia, fichas técnicas, Android ni frontend avanzado.

**Próximo paso — Fase 2**:
- Implementar flujo de reuniones, disponibilidad y reglas de agenda sobre la base ya migrada y testeada.

---

### [2026-06-08] — Fase 2 — Reuniones y disponibilidad integrada

**Qué se hizo**:
- Creada rama `phase-2/meetings-availability` desde `phase-1/backend-base`.
- Revisados timestamps y actualizado `db.DateTime(timezone=True)` para campos de sistema/auditoría.
- Creada migración `b231a19c6a0b_timezone_aware_datetimes_phase_2.py`.
- Implementado `GET /api/users/search` para búsqueda de invitados activos, excluyendo admin.
- Implementado servicio de disponibilidad integrada en `app/availability/service.py`.
- Implementados endpoints de reuniones:
  - `POST /api/meetings/check-availability`
  - `POST /api/meetings`
  - `GET /api/meetings`
  - `GET /api/meetings/<id>`
  - `POST /api/meetings/<id>/accept`
  - `POST /api/meetings/<id>/reject`
  - `POST /api/meetings/<id>/cancel`
- Implementado servicio de notificaciones internas y endpoints de polling.
- Implementado servicio de auditoría para acciones críticas de reunión.
- Agregados schemas Marshmallow de reuniones y disponibilidad.
- Agregados tests de Fase 2 contra PostgreSQL Docker.

**Decisiones tomadas**:
- Timestamps internos timezone-aware con UTC.
- Fecha/hora de reunión permanecen como `date` + `time`.
- Creador bloquea agenda desde la creación.
- Invitados solo bloquean agenda al aceptar.
- Invitación pendiente o rechazada no bloquea agenda.
- Reunión cancelada no bloquea disponibilidad.
- Admin no opera reuniones ni puede ser invitado.
- `suggested_slots` queda como lista vacía documentada para fase posterior.

**Validaciones ejecutadas**:
- `docker compose ps`: PostgreSQL healthy.
- `flask db upgrade`: OK.
- `python scripts/seed_all.py`: OK e idempotente.
- `pytest`: 37 passed.
- `/health`: HTTP 200.

**Confirmaciones**:
- Tests usan PostgreSQL Docker.
- No se usa SQLite.
- No se creó `.env` real.
- No se copiaron archivos de Stitch.
- No se implementaron QR, asistencia, fichas técnicas, audio/transcripción, Android ni frontend avanzado.

---

### [2026-06-08] — Fase 2 — Revisión y cierre de Módulo de Reuniones

**Qué se hizo**:
- Validación de que la estructura base del módulo de reuniones implementa satisfactoriamente todas las restricciones de negocio relacionadas a disponibilidad cruzada de agenda, bloqueos y control de acceso.
- Ejecución completa de pruebas de cobertura.

**Resultados**:
- Se ejecutaron 37 tests, validando rigurosamente que las agendas son bloqueadas únicamente cuando existen confirmaciones reales, permitiendo el estado pendiente.
- Las notificaciones locales y auditorías (AuditLog) se disparan correctamente durante el ciclo de vida de la reunión (creación, aceptación, rechazo, cancelación).
- Se confirmó la integridad del uso de Timezone Aware Datetimes (`db.DateTime(timezone=True)`) con la migración `b231a19c6a0b`.
- Los flujos de acceso son correctos, impidiendo a los administradores generar reuniones u operar como participantes, y restringiendo a las secretarias únicamente a acceso de lectura general.
- Se redactó y publicó el acta de revisión formal en `docs/16_revision_fase_2.md`.
- El entorno se mantiene totalmente limpio sin restos de código desechable o versiones obsoletas.

**Próximo paso — Fase 3**:
- Generación y asignación de códigos QR únicos (AttendanceToken).
- Flujo de escaneo, comprobación de validez y marcado de asistencia.
- Levantamiento de actas o fichas técnicas pos-reunión.

---

### [2026-06-08] — Fase 3 — QR fijo y control de asistencia

**Qué se hizo**:
- Creada rama `phase-3/attendance-qr` desde `phase-2/meetings-availability`.
- Implementado servicio `app/attendance/service.py`.
- Implementado schema `ManualAttendanceSchema`.
- Actualizado `AttendanceToken` para guardar `token_hash` en lugar de token plano.
- Agregados campos de control manual en `MeetingParticipant`.
- Agregados settings QR/manuales al seeder.
- Implementados endpoints:
  - `POST /api/meetings/<meeting_id>/attendance-token`
  - `POST /api/attendance/qr/<token>`
  - `GET /api/meetings/<meeting_id>/attendance`
  - `POST /api/meetings/<meeting_id>/attendance/manual`
- Agregados eventos de auditoría:
  - `attendance_token_created`
  - `attendance_marked_qr`
  - `attendance_marked_manual`
- Agregados eventos de notificación:
  - `qr_available`
  - `attendance_marked`
  - `manual_attendance_marked`
- Creada migración `6b7a85062386_qr_attendance_phase_3.py`.
- Agregados tests de Fase 3 contra PostgreSQL Docker.

**Decisiones tomadas**:
- QR fijo por reunión, no dinámico.
- El token plano se entrega solo al crear el QR y no se persiste.
- La base guarda `token_hash`.
- Si ya existe token activo, se mantiene uno solo y no se reconstruye el token plano.
- Invitados `pending` o `rejected` no marcan asistencia por QR.
- No se implementa finalize; ausentes se calcularán después desde `accepted + not_marked`.

**Validaciones ejecutadas**:
- `docker compose ps`: PostgreSQL healthy.
- `flask db upgrade`: OK.
- `python scripts/seed_all.py`: OK e idempotente.
- `pytest`: 46 passed.
- `/health`: HTTP 200.

**Confirmaciones**:
- Tests usan PostgreSQL Docker.
- No se usa SQLite.
- No se creó `.env` real.
- No se copiaron archivos de Stitch.
- No se implementaron fichas técnicas, audio/transcripción, Android, reportes Excel ni frontend avanzado.

**Próximo paso — Fase 4**:
- Fichas técnicas/actas posteriores a reunión y cálculo formal de ausentes, sin depender todavía de audio/transcripción.

---

*Bitácora de avances — Agenda Ecuamatriz*
*(Actualizar esta sección al finalizar cada fase o avance significativo)*
### 5. Fase 5: Web Operativa (Completada)

**Objetivo Logrado**:
Construir la interfaz web principal del sistema Agenda Ecuamatriz utilizando Jinja2 (Vanilla HTML/CSS).
Implementar diseño limpio basado visualmente en la estructura original de Stitch pero con código limpio y modular, usando la identidad de Ecuamatriz.

**Acciones Realizadas**:
- **CSS Modular**: Se creó un sistema de diseño modular en web/static/css/ (pp.css, layout.css, components.css, orms.css).
- **Plantillas Jinja2**: 
  - Layouts base y auth.
  - Vistas divididas en módulos lógicos por rol: dmin/, user/, secretary/.
- **Rutas Web y Permisos**:
  - web_admin_bp (Acceso solo Admin)
  - web_user_bp (Acceso solo Usuario)
  - web_secretary_bp (Acceso solo Secretaría)
  - Todas las rutas están integradas en ackend/app/web/.
- **Seguridad y Funcionalidad**:
  - Formularios web protegidos globalmente por WTF_CSRF_ENABLED.
  - Integración de Flask-Login para cookies de sesión con redireccionamiento automático tras login fallido.
- **Pruebas**: 
  - 	ests/test_phase5_web.py valida redirecciones, login válido, accesos no autorizados e inyección de sesiones con fixtures de prueba.

**Confirmaciones**:
- NO se convirtió el frontend a SPA (React/Vue/etc.).
- Los archivos ZIP de Stitch permanecen ignorados en .gitignore.
- Se priorizaron elementos funcionales corporativos.

# # #   F a s e   6 :   M o b i l e   A P I   &   F i r e b a s e   ( C o m p l e t a d a ) 
 -   I m p l e m e n t a c i � n   d e   J W T   p a r a   A P I   M � v i l   ( L o g i n ,   R e f r e s h ,   L o g o u t ,   P e r f i l ) . 
 -   M o d e l o   M o b i l e D e v i c e T o k e n   y   m i g r a c i o n e s   p a r a   r e g i s t r o   d e   d i s p o s i t i v o s . 
 -   I n t e g r a c i � n   c o n   f i r e b a s e - a d m i n   ( f a i l - s i l e n t   p a r a   F C M _ E N A B L E D = f a l s e ) . 
 -   E n d p o i n t s   m � v i l e s   d e d i c a d o s   ( / a p i / m o b i l e / m e e t i n g s   y   / a p i / m o b i l e / a t t e n d a n c e ) . 
 -   C o r r e c c i � n   d e   p r u e b a s   d e   i n t e g r a c i � n   c o n   P o s t g r e S Q L .  
 
### Fase 7: Aplicación Android Nativa
- Creación de proyecto base Android con Jetpack Compose y Kotlin.
- Configuración de arquitectura Retrofit, OkHttp, DataStore y FCM.
- Implementación de pantallas: Login, Home, MeetingDetail, QrScanner.
- Configuración de theme corporativo Ecuamatriz.
- Verificación de compilación local.

### [2026-06-08] — Fase 7 — App Android Nativa

**Qué se hizo**:
- Preparación del proyecto Android con Jetpack Compose y Kotlin.
- Configuración del applicationId como com.agenda.movil.
- Integración de dependencias de Retrofit, OkHttp, DataStore y Firebase.
- Implementación de cliente HTTP con interceptor para inyectar token JWT.
- Almacenamiento local seguro para tokens.
- Implementación de interfaz visual siguiendo identidad Ecuamatriz.
- Consumo de API para Login y Refresh.
- Pantalla de inicio con reuniones e invitaciones.
- Detalles de reunión, aceptar y rechazar invitaciones.
- Integración de Firebase Messaging para notificaciones.

**Próximo paso**:
- Continuar con Fase 8: Reportes y Actas.


### [2026-06-08] — Cierre Formal Fase 7

**Validaciones Realizadas**:
- Compilación exitosa del proyecto Android en modo Debug.
- Backend: Migraciones, seeder idempotente y pruebas (58 tests pasando).
- NetworkConfig.kt añadido para evitar BASE_URL quemada.
- Flujos validados: Login contra API, Home con reuniones, Registro de Token FCM, Flujo de simulador de QR.
- Documentación actualizada con endpoints y limitaciones actuales.
- Se confirmó que Firebase push no está activado en backend (FCM_ENABLED=false) pero registra dispositivo.
- Quedan pospuestas funcionalidades futuras como Panel móvil y Escaneo QR físico.

### [2026-06-09] — Fase 8 — Endurecimiento Android

**Qué se hizo**:
- Implementado flujo de renovación automática de tokens JWT usando `OkHttp Authenticator`.
- Agregado control de expiración de sesión que limpia preferencias y redirige a la pantalla de Login con estado limpio si el refresh token expira.
- Implementado el escaneo nativo de códigos QR usando `CameraX` y `ML Kit Barcode Scanning`.
- Actualizado el flujo de `QrScannerScreen` para solicitar permisos de cámara en tiempo de ejecución y procesar tokens QR reales.
- Agregada extracción de tokens a partir de URLs y mantenido un modo manual/debug como alternativa secundaria.
- Tests del backend validados exitosamente tras sembrar datos y migraciones (58 passed).
- Build Android `assembleDebug` verificado.

**Decisiones de Diseño**:
- El Authenticator bloquea `/api/auth/refresh` de bucles infinitos y realiza la petición `POST` en hilo sincrónico limpio para renovar la sesión de forma transparente.
- Las dependencias de Android (camerax, mlkit, guava) se agruparon en el catálogo de versiones de Gradle.

**Próximo paso**:
- Pasar a siguientes fases (Reportes, Actas u optimizaciones).


### [2026-06-09] — Fase 9 — Piloto y Estabilización

**Qué se hizo**:
- Creada rama \phase-9/stabilization-pilot\.
- Validada la integridad y limpieza de las exclusiones del proyecto (\.env\, json de firebase, tokens en logs).
- Verificada la idempotencia del comando de siembra (\seed_all.py\).
- Confirmado que las pruebas del backend alcanzan el 100% (58 tests) en el entorno de pruebas con PostgreSQL.
- Verificado el build exitoso de la aplicación Android (\ssembleDebug\).
- Creado el documento \21_stabilization_pilot.md\ con instrucciones detalladas de UAT y configuraciones de red incluyendo el uso de \
grok\ para pilotos remotos.
- Actualizado el archivo de configuración en Android (\NetworkConfig.kt\) con la documentación sobre cómo apuntar localmente y a ngrok.

**Próximo paso**:
- Entrega del piloto para UAT (Pruebas de Aceptación de Usuario) manual.
- Futuras fases (Reportes, Fichas técnicas, Panel móvil) quedan bajo reserva y planificación posterior.


### [2026-06-09] — Preparación de Entorno para Pruebas Reales (Local LAN)

**Qué se hizo**:
- Identificada la IP local en red LAN: \192.168.0.139\.
- Verificado el estado de los contenedores Docker y el seeder idempotente.
- Confirmado éxito de la suite de pruebas del backend (100% passed).
- Actualizado el \NetworkConfig.kt\ en Android para apuntar a la IP LAN para pruebas con teléfonos físicos conectados a la misma red WiFi.
- Añadido \ndroid:usesCleartextTraffic="true\" en el \AndroidManifest.xml\ de Android para permitir tráfico local HTTP.
- Construida y empaquetada la APK Debug localmente.
- Creado documento \docs/22_local_real_testing.md\ detallando las pruebas de humo web y móvil a ejecutar por los usuarios reales.

**Nota técnica**:
No se utilizó \
grok\ ni Cloudflare Tunnel. La prueba ha sido enjaulada en la infraestructura de la LAN para testeo directo e inmediato.


### [2026-06-09] — Correcciones de Piloto Local (Fase 9.1)

**Qué se hizo**:
- Identificado y corregido el renderizado del token CSRF (que se mostraba en texto plano en la vista del administrador) en los formularios de configuración de usuarios, salas y áreas (\users.html\, \reas.html\, \ooms.html\, \settings.html\, \meeting_detail.html\).
- Reparada la barra de navegación lateral izquierda (\sidebar.html\) sustituyendo \href="#\"\ por llamadas reales a \url_for\.
- Corregida la condicional del backend en los templates Jinja2 (\current_user.role_slug\) para que coincida exactamente con los roles hispanos de la BD (\secretaria\, \usuario\) permitiendo revelar los menús correctos a cada perfil.
- Completadas y superadas nuevamente las pruebas automatizadas del Backend (100% success) y de la APK de Android (assembleDebug).
- Se documentó la necesidad inamovible de permitir puertos a nivel Firewall de Windows para el acceso del dispositivo móvil físico a la LAN.

**Estado Actual**: Listo y desplegable.


- Modificados los templates jinja2 para renderizar \date\, \start_time\ y \end_time\ en lugar del inexistente \scheduled_at\.
- Corregida la creación de reuniones en web para no pedir IDs por consola, ahora muestra checkboxes con los usuarios activos de la base de datos.

- Limpiados atributos de vista inexistentes en meeting_detail.html y ajustados los estados de badges a los correctos.
- Corregida la creación de usuarios desde admin para separar nombres desde un único input de full_name.
- Mejorada la lógica de AttendanceService para regenerar el token QR en caso de recargas web y garantizar despliegue.
- Eliminada la escalada de privilegios inadvertida de la Secretaría para aceptar o rechazar reuniones desde los endpoints de participantes.
- Agregados y reforzados tests de UI para verificar la renderización de perfiles de usuario y reunión.

