# 13 â€” BitÃ¡cora de Avances

## Formato de entrada

```
### [YYYY-MM-DD] â€” Fase X â€” DescripciÃ³n del avance
- QuÃ© se hizo
- Decisiones tomadas
- Problemas encontrados
- PrÃ³ximo paso
```

---

## Entradas

---

### [2026-06-09] — Fase 9 — Estabilización Piloto y Agenda Unificada Móvil
- Se unificó la agenda móvil combinando las pestañas separadas "Hoy" y "Próximas" en una única pestaña "Agenda" ordenada cronológicamente.
- Se implementó la creación de reuniones directamente desde la aplicación Android, con selección de sala y participantes.
- Se estableció por diseño que el rol Secretaría actúa exclusivamente como usuario operativo dentro de la aplicación móvil, relegando la supervisión institucional al panel web.
- Se implementó bloqueo explícito para el rol Administrador al intentar ingresar por móvil (HTTP 403 con mensaje de error controlado).
- Se implementó un polling liviano cada 15 segundos en `AgendaScreen` para mantener las listas actualizadas.
- Se actualizaron y comprobaron todos los tests de API en pytest, y se compiló exitosamente el nuevo APK para Android.

---

### [2026-06-07] â€” Fase 0 â€” Estructura inicial del proyecto

**QuÃ© se hizo**:
- Reinicio completo del proyecto desde cero.
- Creada la estructura de carpetas completa del proyecto.
- Creado `.gitignore` para Python/Flask/Android/Node.
- Creado `.env.example` sin secretos.
- Creado `README.md` con descripciÃ³n completa del sistema.
- Creada la Application Factory de Flask con todos los blueprints registrados.
- Creados los `__init__.py` de los 17 mÃ³dulos del backend con su docstring de responsabilidades.
- Creados los `routes.py` de todos los mÃ³dulos con stubs documentados y indicaciÃ³n de fase.
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
- Creado `app/shared/decorators.py` con decoradores de autorizaciÃ³n por rol.
- Creado `tests/conftest.py` con fixtures de pytest.
- Creado `tests/test_health.py` con tests de sanidad.
- Creado `scripts/seed_all.py` con seeder idempotente.
- Creados los 14 documentos de `docs/` (00 a 13).

**Decisiones tomadas**:
- **No usar SPA en primera versiÃ³n.** Se usa Flask + Jinja2 para mayor control y simplicidad.
- **QR fijo** (no rotativo) en primera versiÃ³n. MÃ¡s simple, suficiente para el contexto.
- **JWT** como mecanismo de autenticaciÃ³n (no sesiones Flask).
- **Marshmallow** para validaciÃ³n y serializaciÃ³n (no Pydantic).
- **Un solo flujo de reuniÃ³n.** No tipos de reuniÃ³n.
- **SecretarÃ­a no es cuello de botella.** No aprueba reuniones.
- **Admin no participa en reuniones.** Rol tÃ©cnico puro.
- **MÃ³dulos recordings y transcriptions** creados como stubs para no bloquear Fase 8.
- **SQLite en tests**, PostgreSQL en desarrollo y producciÃ³n.

**Herramientas elegidas**:
- `qrcode[pil]` para generaciÃ³n de QR (Python).
- `openpyxl` para exportaciÃ³n Excel.
- `firebase-admin` para FCM (notificaciones push Android).
- `pytest + pytest-flask` para tests.
- `flask-migrate + alembic` para migraciones.

**PrÃ³ximo paso**:
- **Fase 1**: Implementar backend base.
  - Crear la migraciÃ³n inicial (`flask db migrate -m "initial schema"`).
  - Implementar `auth` (login web y API JWT).
  - Implementar `users` (CRUD + bÃºsqueda).
  - Implementar `areas`, `rooms`, `settings`.
  - Ejecutar seeder y verificar.
  - Escribir tests de cada mÃ³dulo.

---

### [2026-06-08] â€” Fase 0 â€” RevisiÃ³n y ajuste de cierre

**QuÃ© se hizo**:
- AuditorÃ­a tÃ©cnica completa antes de cerrar Fase 0.
- CorrecciÃ³n de decisiones preliminares que hubieran generado deuda.

**Decisiones definitivas tomadas**:

**AutenticaciÃ³n â€” dos canales:**
- **Web (Jinja2)**: Flask-Login con sesiones de servidor y cookies seguras.
  Blueprint `auth_web_bp` en `session_routes.py` â†’ `/auth/`
- **API mÃ³vil (Android)**: JWT con Flask-JWT-Extended.
  Blueprint `auth_api_bp` en `api_routes.py` â†’ `/api/auth/`
- Regla: la web NUNCA usa JWT. La API NUNCA usa sesiones Flask.
- Ambos blueprints comparten `AuthService.authenticate()`.

**Base de datos:**
- PostgreSQL Docker desde el inicio, incluyendo tests.
- SQLite eliminado completamente del proyecto.
- Driver cambiado: `psycopg2-binary` â†’ `psycopg[binary]` (v3).
- BD desarrollo: `agenda_ecuamatriz`. BD test: `agenda_ecuamatriz_test`.

**Infraestructura:**
- Creado `docker-compose.yml` con `postgres:16-alpine` + healthcheck + volumen persistente.
- Creado `docker/postgres/init.sql` que crea la BD de test automÃ¡ticamente.

**User model:**
- Actualizado para implementar `flask_login.UserMixin`.
- `get_id()` explÃ­cito. `is_active` hace override al de UserMixin.

**Tests:**
- `conftest.py` reescrito: PostgreSQL obligatorio, falla con mensaje claro si detecta SQLite.
- Fixture `db_session` con rollback por test para aislamiento.
- Fixture `secretary_user` aÃ±adida (faltaba).
- `test_health.py` actualizado para verificar `/health`, `auth_web_bp` y `auth_api_bp`.
- `pytest.ini` creado.

**Seeder:**
- Orden corregido: roles â†’ Ã¡reas â†’ salas â†’ usuarios â†’ settings.
- 3 usuarios demo con emails `.local`.
- Ã�reas actualizadas: AdministraciÃ³n, Gerencia, ProducciÃ³n, Ventas, Sistemas, Talento Humano, Finanzas, Legal.
- Salas: Sala Principal, Sala Reuniones 1, Sala Reuniones 2.
- Setting `notifications_enabled` aÃ±adido.

**DocumentaciÃ³n:**
- Creado `docs/14_revision_fase_0.md` con decisiones, checklist y prÃ³ximos pasos.
- `.env.example` actualizado con nuevas variables.
- `requirements.txt` actualizado.

**Archivos creados/modificados en esta revisiÃ³n**:
- `docker-compose.yml` (nuevo)
- `docker/postgres/init.sql` (nuevo)
- `.env.example` (actualizado)
- `backend/requirements.txt` (actualizado)
- `backend/app/__init__.py` (actualizado â€” Flask-Login, CSRF, /health)
- `backend/app/users/models.py` (actualizado â€” UserMixin)
- `backend/app/auth/session_routes.py` (nuevo)
- `backend/app/auth/api_routes.py` (nuevo)
- `backend/app/auth/service.py` (nuevo â€” stub)
- `backend/app/auth/routes.py` (convertido en doc)
- `backend/tests/conftest.py` (reescrito â€” PostgreSQL)
- `backend/tests/test_health.py` (actualizado)
- `backend/pytest.ini` (nuevo)
- `backend/scripts/seed_all.py` (actualizado)
- `docs/14_revision_fase_0.md` (nuevo)
- `.gitignore` (actualizado â€” docker, tests/tmp)

**Problemas encontrados**: Ninguno crÃ­tico. Los cambios son preventivos.

**PrÃ³ximo paso â€” Fase 1**:
1. `docker compose up -d`
2. Crear `venv`, instalar `requirements.txt`
3. Configurar `.env`
4. `flask db init` + `flask db migrate -m "initial schema"` + `flask db upgrade`
5. `python scripts/seed_all.py`
6. Implementar `auth/service.py` â†’ `session_routes.py` â†’ `api_routes.py`
7. Implementar `users/`, `areas/`, `rooms/`, `settings/`
8. Escribir tests. Ejecutar `pytest`.

---

### [2026-06-08] â€” Fase 0 â€” Bootstrap Git y estabilizaciÃ³n final

**QuÃ© se hizo**:
- Inicializado repositorio Git local en `D:\Agenda_Ecuamatriz`.
- Configurada rama principal `main`.
- Configurado remoto `origin` hacia `https://github.com/Pega-568/Agenda_Ecuamatriz.git`.
- Creada rama de trabajo `phase-0/bootstrap`.
- Endurecido `.gitignore` para excluir explÃ­citamente `stitch_*.zip`, `*.html`, `.env`, `venv/`, `__pycache__/`, `.pytest_cache/`, `node_modules/`, `dist/`, `build/`, APK y bases SQLite/DB.
- Corregido el error ORM que impedÃ­a ejecutar pytest:
  - `backend/app/__init__.py` ahora registra/importa todos los modelos antes de migraciones/tests.
  - `AuditLog.metadata` se renombrÃ³ a atributo Python `metadata_json`, conservando la columna `"metadata"`.

**Validaciones ejecutadas**:
- `docker compose ps`: `agenda_ecuamatriz_db` healthy.
- `SELECT 1` en `agenda_ecuamatriz`: OK.
- `SELECT 1` en `agenda_ecuamatriz_test`: OK.
- `pytest`: 6 passed, 2 warnings de deprecaciÃ³n por `datetime.utcnow()`.
- `/health`: `{"app":"Agenda Ecuamatriz","database":"ok","status":"ok"}`.

**Confirmaciones**:
- `pytest` usa PostgreSQL Docker mediante `TEST_DATABASE_URL`.
- No usa SQLite.
- No hay error de imports ORM.
- No existe `.env` real.
- No se detectaron secretos reales.
- Los ZIP de Stitch permanecen en filesystem, pero quedan fuera de Git por `.gitignore`.
- No se implementaron funcionalidades de Fase 1.

**PrÃ³ximo paso**:
- Hacer commit `Bootstrap clean Agenda Ecuamatriz phase 0`.
- Hacer push de `phase-0/bootstrap` al remoto.
- No hacer merge a `main` todavÃ­a.

---

### [2026-06-08] â€” Fase 1 â€” Backend base funcional

**QuÃ© se hizo**:
- Creada rama `phase-1/backend-base` desde `phase-0/bootstrap`.
- Implementados servicios base para `auth`, `roles`, `users`, `areas`, `rooms`, `settings` y `calendar/work schedule`.
- Agregados schemas Marshmallow para validaciÃ³n de entradas en usuarios, Ã¡reas, salas, settings y horario laboral.
- Implementado login web con Flask-Login, logout y dashboard mÃ­nimo.
- Preparado login API JWT mÃ­nimo y `/api/auth/me`, separado del login web.
- Agregado modelo `WorkSchedule` para horario laboral semanal.
- Inicializado Flask-Migrate/Alembic y creada migraciÃ³n inicial `9f7c5986fbf4_initial_schema_phase_1.py`.
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
- No se creÃ³ `.env` real.
- No se implementaron reuniones, QR, asistencia, fichas tÃ©cnicas, Android ni frontend avanzado.

**PrÃ³ximo paso â€” Fase 2**:
- Implementar flujo de reuniones, disponibilidad y reglas de agenda sobre la base ya migrada y testeada.

---

### [2026-06-08] â€” Fase 2 â€” Reuniones y disponibilidad integrada

**QuÃ© se hizo**:
- Creada rama `phase-2/meetings-availability` desde `phase-1/backend-base`.
- Revisados timestamps y actualizado `db.DateTime(timezone=True)` para campos de sistema/auditorÃ­a.
- Creada migraciÃ³n `b231a19c6a0b_timezone_aware_datetimes_phase_2.py`.
- Implementado `GET /api/users/search` para bÃºsqueda de invitados activos, excluyendo admin.
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
- Implementado servicio de auditorÃ­a para acciones crÃ­ticas de reuniÃ³n.
- Agregados schemas Marshmallow de reuniones y disponibilidad.
- Agregados tests de Fase 2 contra PostgreSQL Docker.

**Decisiones tomadas**:
- Timestamps internos timezone-aware con UTC.
- Fecha/hora de reuniÃ³n permanecen como `date` + `time`.
- Creador bloquea agenda desde la creaciÃ³n.
- Invitados solo bloquean agenda al aceptar.
- InvitaciÃ³n pendiente o rechazada no bloquea agenda.
- ReuniÃ³n cancelada no bloquea disponibilidad.
- Admin no opera reuniones ni puede ser invitado.
- `suggested_slots` queda como lista vacÃ­a documentada para fase posterior.

**Validaciones ejecutadas**:
- `docker compose ps`: PostgreSQL healthy.
- `flask db upgrade`: OK.
- `python scripts/seed_all.py`: OK e idempotente.
- `pytest`: 37 passed.
- `/health`: HTTP 200.

**Confirmaciones**:
- Tests usan PostgreSQL Docker.
- No se usa SQLite.
- No se creÃ³ `.env` real.
- No se copiaron archivos de Stitch.
- No se implementaron QR, asistencia, fichas tÃ©cnicas, audio/transcripciÃ³n, Android ni frontend avanzado.

---

### [2026-06-08] â€” Fase 2 â€” RevisiÃ³n y cierre de MÃ³dulo de Reuniones

**QuÃ© se hizo**:
- ValidaciÃ³n de que la estructura base del mÃ³dulo de reuniones implementa satisfactoriamente todas las restricciones de negocio relacionadas a disponibilidad cruzada de agenda, bloqueos y control de acceso.
- EjecuciÃ³n completa de pruebas de cobertura.

**Resultados**:
- Se ejecutaron 37 tests, validando rigurosamente que las agendas son bloqueadas Ãºnicamente cuando existen confirmaciones reales, permitiendo el estado pendiente.
- Las notificaciones locales y auditorÃ­as (AuditLog) se disparan correctamente durante el ciclo de vida de la reuniÃ³n (creaciÃ³n, aceptaciÃ³n, rechazo, cancelaciÃ³n).
- Se confirmÃ³ la integridad del uso de Timezone Aware Datetimes (`db.DateTime(timezone=True)`) con la migraciÃ³n `b231a19c6a0b`.
- Los flujos de acceso son correctos, impidiendo a los administradores generar reuniones u operar como participantes, y restringiendo a las secretarias Ãºnicamente a acceso de lectura general.
- Se redactÃ³ y publicÃ³ el acta de revisiÃ³n formal en `docs/16_revision_fase_2.md`.
- El entorno se mantiene totalmente limpio sin restos de cÃ³digo desechable o versiones obsoletas.

**PrÃ³ximo paso â€” Fase 3**:
- GeneraciÃ³n y asignaciÃ³n de cÃ³digos QR Ãºnicos (AttendanceToken).
- Flujo de escaneo, comprobaciÃ³n de validez y marcado de asistencia.
- Levantamiento de actas o fichas tÃ©cnicas pos-reuniÃ³n.

---

### [2026-06-08] â€” Fase 3 â€” QR fijo y control de asistencia

**QuÃ© se hizo**:
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
- Agregados eventos de auditorÃ­a:
  - `attendance_token_created`
  - `attendance_marked_qr`
  - `attendance_marked_manual`
- Agregados eventos de notificaciÃ³n:
  - `qr_available`
  - `attendance_marked`
  - `manual_attendance_marked`
- Creada migraciÃ³n `6b7a85062386_qr_attendance_phase_3.py`.
- Agregados tests de Fase 3 contra PostgreSQL Docker.

**Decisiones tomadas**:
- QR fijo por reuniÃ³n, no dinÃ¡mico.
- El token plano se entrega solo al crear el QR y no se persiste.
- La base guarda `token_hash`.
- Si ya existe token activo, se mantiene uno solo y no se reconstruye el token plano.
- Invitados `pending` o `rejected` no marcan asistencia por QR.
- No se implementa finalize; ausentes se calcularÃ¡n despuÃ©s desde `accepted + not_marked`.

**Validaciones ejecutadas**:
- `docker compose ps`: PostgreSQL healthy.
- `flask db upgrade`: OK.
- `python scripts/seed_all.py`: OK e idempotente.
- `pytest`: 46 passed.
- `/health`: HTTP 200.

**Confirmaciones**:
- Tests usan PostgreSQL Docker.
- No se usa SQLite.
- No se creÃ³ `.env` real.
- No se copiaron archivos de Stitch.
- No se implementaron fichas tÃ©cnicas, audio/transcripciÃ³n, Android, reportes Excel ni frontend avanzado.

**PrÃ³ximo paso â€” Fase 4**:
- Fichas tÃ©cnicas/actas posteriores a reuniÃ³n y cÃ¡lculo formal de ausentes, sin depender todavÃ­a de audio/transcripciÃ³n.

---

*BitÃ¡cora de avances â€” Agenda Ecuamatriz*
*(Actualizar esta secciÃ³n al finalizar cada fase o avance significativo)*
### 5. Fase 5: Web Operativa (Completada)

**Objetivo Logrado**:
Construir la interfaz web principal del sistema Agenda Ecuamatriz utilizando Jinja2 (Vanilla HTML/CSS).
Implementar diseÃ±o limpio basado visualmente en la estructura original de Stitch pero con cÃ³digo limpio y modular, usando la identidad de Ecuamatriz.

**Acciones Realizadas**:
- **CSS Modular**: Se creÃ³ un sistema de diseÃ±o modular en web/static/css/ (pp.css, layout.css, components.css, orms.css).
- **Plantillas Jinja2**: 
  - Layouts base y auth.
  - Vistas divididas en mÃ³dulos lÃ³gicos por rol: dmin/, user/, secretary/.
- **Rutas Web y Permisos**:
  - web_admin_bp (Acceso solo Admin)
  - web_user_bp (Acceso solo Usuario)
  - web_secretary_bp (Acceso solo SecretarÃ­a)
  - Todas las rutas estÃ¡n integradas en ackend/app/web/.
- **Seguridad y Funcionalidad**:
  - Formularios web protegidos globalmente por WTF_CSRF_ENABLED.
  - IntegraciÃ³n de Flask-Login para cookies de sesiÃ³n con redireccionamiento automÃ¡tico tras login fallido.
- **Pruebas**: 
  - 	ests/test_phase5_web.py valida redirecciones, login vÃ¡lido, accesos no autorizados e inyecciÃ³n de sesiones con fixtures de prueba.

**Confirmaciones**:
- NO se convirtiÃ³ el frontend a SPA (React/Vue/etc.).
- Los archivos ZIP de Stitch permanecen ignorados en .gitignore.
- Se priorizaron elementos funcionales corporativos.

# # #   F a s e   6 :   M o b i l e   A P I   &   F i r e b a s e   ( C o m p l e t a d a ) 
 -   I m p l e m e n t a c i ó n   d e   J W T   p a r a   A P I   M ó v i l   ( L o g i n ,   R e f r e s h ,   L o g o u t ,   P e r f i l ) . 
 -   M o d e l o   M o b i l e D e v i c e T o k e n   y   m i g r a c i o n e s   p a r a   r e g i s t r o   d e   d i s p o s i t i v o s . 
 -   I n t e g r a c i ó n   c o n   f i r e b a s e - a d m i n   ( f a i l - s i l e n t   p a r a   F C M _ E N A B L E D = f a l s e ) . 
 -   E n d p o i n t s   m ó v i l e s   d e d i c a d o s   ( / a p i / m o b i l e / m e e t i n g s   y   / a p i / m o b i l e / a t t e n d a n c e ) . 
 -   C o r r e c c i ó n   d e   p r u e b a s   d e   i n t e g r a c i ó n   c o n   P o s t g r e S Q L .  
 
### Fase 7: AplicaciÃ³n Android Nativa
- CreaciÃ³n de proyecto base Android con Jetpack Compose y Kotlin.
- ConfiguraciÃ³n de arquitectura Retrofit, OkHttp, DataStore y FCM.
- ImplementaciÃ³n de pantallas: Login, Home, MeetingDetail, QrScanner.
- ConfiguraciÃ³n de theme corporativo Ecuamatriz.
- VerificaciÃ³n de compilaciÃ³n local.

### [2026-06-08] â€” Fase 7 â€” App Android Nativa

**QuÃ© se hizo**:
- PreparaciÃ³n del proyecto Android con Jetpack Compose y Kotlin.
- ConfiguraciÃ³n del applicationId como com.agenda.movil.
- IntegraciÃ³n de dependencias de Retrofit, OkHttp, DataStore y Firebase.
- ImplementaciÃ³n de cliente HTTP con interceptor para inyectar token JWT.
- Almacenamiento local seguro para tokens.
- ImplementaciÃ³n de interfaz visual siguiendo identidad Ecuamatriz.
- Consumo de API para Login y Refresh.
- Pantalla de inicio con reuniones e invitaciones.
- Detalles de reuniÃ³n, aceptar y rechazar invitaciones.
- IntegraciÃ³n de Firebase Messaging para notificaciones.

**PrÃ³ximo paso**:
- Continuar con Fase 8: Reportes y Actas.


### [2026-06-08] â€” Cierre Formal Fase 7

**Validaciones Realizadas**:
- CompilaciÃ³n exitosa del proyecto Android en modo Debug.
- Backend: Migraciones, seeder idempotente y pruebas (58 tests pasando).
- NetworkConfig.kt aÃ±adido para evitar BASE_URL quemada.
- Flujos validados: Login contra API, Home con reuniones, Registro de Token FCM, Flujo de simulador de QR.
- DocumentaciÃ³n actualizada con endpoints y limitaciones actuales.
- Se confirmÃ³ que Firebase push no estÃ¡ activado en backend (FCM_ENABLED=false) pero registra dispositivo.
- Quedan pospuestas funcionalidades futuras como Panel mÃ³vil y Escaneo QR fÃ­sico.

### [2026-06-09] â€” Fase 8 â€” Endurecimiento Android

**QuÃ© se hizo**:
- Implementado flujo de renovaciÃ³n automÃ¡tica de tokens JWT usando `OkHttp Authenticator`.
- Agregado control de expiraciÃ³n de sesiÃ³n que limpia preferencias y redirige a la pantalla de Login con estado limpio si el refresh token expira.
- Implementado el escaneo nativo de cÃ³digos QR usando `CameraX` y `ML Kit Barcode Scanning`.
- Actualizado el flujo de `QrScannerScreen` para solicitar permisos de cÃ¡mara en tiempo de ejecuciÃ³n y procesar tokens QR reales.
- Agregada extracciÃ³n de tokens a partir de URLs y mantenido un modo manual/debug como alternativa secundaria.
- Tests del backend validados exitosamente tras sembrar datos y migraciones (58 passed).
- Build Android `assembleDebug` verificado.

**Decisiones de DiseÃ±o**:
- El Authenticator bloquea `/api/auth/refresh` de bucles infinitos y realiza la peticiÃ³n `POST` en hilo sincrÃ³nico limpio para renovar la sesiÃ³n de forma transparente.
- Las dependencias de Android (camerax, mlkit, guava) se agruparon en el catÃ¡logo de versiones de Gradle.

**PrÃ³ximo paso**:
- Pasar a siguientes fases (Reportes, Actas u optimizaciones).


### [2026-06-09] â€” Fase 9 â€” Piloto y EstabilizaciÃ³n

**QuÃ© se hizo**:
- Creada rama \phase-9/stabilization-pilot\.
- Validada la integridad y limpieza de las exclusiones del proyecto (\.env\, json de firebase, tokens en logs).
- Verificada la idempotencia del comando de siembra (\seed_all.py\).
- Confirmado que las pruebas del backend alcanzan el 100% (58 tests) en el entorno de pruebas con PostgreSQL.
- Verificado el build exitoso de la aplicaciÃ³n Android (\ssembleDebug\).
- Creado el documento \21_stabilization_pilot.md\ con instrucciones detalladas de UAT y configuraciones de red incluyendo el uso de \
grok\ para pilotos remotos.
- Actualizado el archivo de configuraciÃ³n en Android (\NetworkConfig.kt\) con la documentaciÃ³n sobre cÃ³mo apuntar localmente y a ngrok.

**PrÃ³ximo paso**:
- Entrega del piloto para UAT (Pruebas de AceptaciÃ³n de Usuario) manual.
- Futuras fases (Reportes, Fichas tÃ©cnicas, Panel mÃ³vil) quedan bajo reserva y planificaciÃ³n posterior.


### [2026-06-09] â€” PreparaciÃ³n de Entorno para Pruebas Reales (Local LAN)

**QuÃ© se hizo**:
- Identificada la IP local en red LAN: \192.168.0.139\.
- Verificado el estado de los contenedores Docker y el seeder idempotente.
- Confirmado Ã©xito de la suite de pruebas del backend (100% passed).
- Actualizado el \NetworkConfig.kt\ en Android para apuntar a la IP LAN para pruebas con telÃ©fonos fÃ­sicos conectados a la misma red WiFi.
- AÃ±adido \ndroid:usesCleartextTraffic="true\" en el \AndroidManifest.xml\ de Android para permitir trÃ¡fico local HTTP.
- Construida y empaquetada la APK Debug localmente.
- Creado documento \docs/22_local_real_testing.md\ detallando las pruebas de humo web y mÃ³vil a ejecutar por los usuarios reales.

**Nota tÃ©cnica**:
No se utilizÃ³ \
grok\ ni Cloudflare Tunnel. La prueba ha sido enjaulada en la infraestructura de la LAN para testeo directo e inmediato.


### [2026-06-09] â€” Correcciones de Piloto Local (Fase 9.1)

**QuÃ© se hizo**:
- Identificado y corregido el renderizado del token CSRF (que se mostraba en texto plano en la vista del administrador) en los formularios de configuraciÃ³n de usuarios, salas y Ã¡reas (\users.html\, \reas.html\, \ooms.html\, \settings.html\, \meeting_detail.html\).
- Reparada la barra de navegaciÃ³n lateral izquierda (\sidebar.html\) sustituyendo \href="#\"\ por llamadas reales a \url_for\.
- Corregida la condicional del backend en los templates Jinja2 (\current_user.role_slug\) para que coincida exactamente con los roles hispanos de la BD (\secretaria\, \usuario\) permitiendo revelar los menÃºs correctos a cada perfil.
- Completadas y superadas nuevamente las pruebas automatizadas del Backend (100% success) y de la APK de Android (assembleDebug).
- Se documentÃ³ la necesidad inamovible de permitir puertos a nivel Firewall de Windows para el acceso del dispositivo mÃ³vil fÃ­sico a la LAN.

**Estado Actual**: Listo y desplegable.


- Modificados los templates jinja2 para renderizar \date\, \start_time\ y \end_time\ en lugar del inexistente \scheduled_at\.
- Corregida la creaciÃ³n de reuniones en web para no pedir IDs por consola, ahora muestra checkboxes con los usuarios activos de la base de datos.

- Limpiados atributos de vista inexistentes en meeting_detail.html y ajustados los estados de badges a los correctos.
- Corregida la creación de usuarios desde admin para separar nombres desde un único input de full_name.
- Mejorada la lógica de AttendanceService para regenerar el token QR en caso de recargas web y garantizar despliegue.
- Eliminada la escalada de privilegios inadvertida de la Secretaría para aceptar o rechazar reuniones desde los endpoints de participantes.
- Agregados y reforzados tests de UI para verificar la renderización de perfiles de usuario y reunión.

### [2026-06-09] — Correcciones de Integración Android-Web-Backend (Fase 9.2)

**Qué se hizo**:
- Añadido soporte dinámico en `MeetingService.to_dict` (al inyectar `current_user`) para que devuelva estados contextuales a la app móvil: `role_in_meeting`, `my_invitation_status`, `my_attendance_status`, `can_accept`, `can_reject`, `can_show_qr`.
- Corregido el manejo de excepciones en `mobile_attendance_bp` para el escaneo de QR. Ahora devuelve explícitamente un código HTTP `400 Bad Request` en caso de errores controlados (`ValueError`) en lugar de `409 Conflict` y mantiene un formato estándar JSON `{"success": false, "error": "mensaje"}`.
- Reparada la llamada a la función correcta de asistencia (`AttendanceService.mark_by_qr`) en lugar de la inexistente `mark_qr` que provocaba un volcado `500 Internal Server Error`.
- Reforzada la extracción de mensajes de error de JSON en Android (`QrScannerScreen.kt`) para buscar adecuadamente dentro del objeto `"error" : { "message": "..." }`.
- Ampliados los DTO en Android (`MeetingResponse.kt`) para abarcar los estados de usuario contextual.
- Habilitados los botones de *Aceptar* y *Rechazar* en la vista `MeetingDetailScreen.kt` de Android que consumen los endpoints respectivos de `AgendaApiService`.
- Agregados los tests automatizados para certificar los flujos de invitaciones aceptadas, invitaciones rechazadas y validaciones de errores de escaneo QR.

**Estado Actual**: Listo y desplegable. Tests 100% pasando y Android APK recompilado con éxito.

