# 11 — Plan de Fases

## Visión general

El sistema se construye en 9 fases progresivas. Cada fase entrega valor funcional y no rompe lo anterior.

---

## Fase 0 — Estructura, documentación y configuración base

**Estado**: ✅ Completada

**Entregables**:
- [x] Árbol de carpetas del proyecto
- [x] README.md
- [x] .gitignore
- [x] .env.example
- [x] Documentación docs/ (00-13)
- [x] Application factory Flask
- [x] Blueprints de todos los módulos (stubs)
- [x] Modelos de datos completos (sin migrar)
- [x] Shared: responses.py, decorators.py
- [x] Estructura de tests (conftest.py, test_health.py)
- [x] Seeder inicial (seed_all.py)

---

## Fase 1 — Backend base

**Objetivo**: Backend funcional con autenticación y gestión de datos maestros.

**Módulos**:
- `auth`: Login, logout, refresh, JWT
- `users`: CRUD usuarios + búsqueda
- `roles`: Listado de roles
- `areas`: CRUD áreas
- `rooms`: CRUD salas
- `settings`: Configuración del sistema (CRUD key-value)
- `calendar`: Validación de fecha laborable (base)
- `audit`: Modelo + función de registro (sin UI)

**Entregables**:
- [ ] Endpoints funcionales con JWT
- [ ] Validaciones con Marshmallow
- [ ] Migración inicial de BD
- [ ] Seeder ejecutable
- [ ] Tests de auth, users, roles, areas, rooms, settings
- [ ] Documentar en bitácora

---

## Fase 2 — Reuniones, invitaciones y notificaciones

**Objetivo**: El flujo completo de creación de reunión funcional en API.

**Módulos**:
- `meetings`: Crear, listar, detalle, cancelar
- `meetings`: Responder invitación (aceptar/rechazar)
- `availability`: Check de disponibilidad integrado
- `notifications`: Crear, listar, marcar como leída (web)

**Entregables**:
- [ ] Flujo completo de nueva reunión via API
- [ ] Validaciones de bloqueo duro y advertencias
- [ ] Notificaciones básicas (invitation, accepted, rejected, cancelled)
- [ ] Tests del flujo de reunión
- [ ] Tests de disponibilidad con casos edge

---

## Fase 3 — Web Usuario

**Objetivo**: Interfaz web funcional para el colaborador interno.

**Pantallas**:
- Dashboard
- Nueva reunión (flujo completo con disponibilidad)
- Mis reuniones
- Invitaciones pendientes
- Detalle de reunión
- Notificaciones

**Entregables**:
- [ ] Layout base con identidad Ecuamatriz
- [ ] Todas las pantallas de usuario funcionales
- [ ] Formulario de nueva reunión con validación
- [ ] Campana de notificaciones funcional
- [ ] Diseño validado contra guía visual

---

## Fase 4 — QR de Asistencia

**Objetivo**: Sistema de asistencia QR funcional.

**Módulos**:
- `attendance`: Generar QR, validar QR, marcar asistencia
- Web: Vista QR para creador
- Web: Escaneo QR básico (si aplica en web)

**Entregables**:
- [ ] Generación QR al crear reunión
- [ ] Validación de todas las condiciones del QR
- [ ] Tests del flujo QR (válido, expirado, fuera de ventana, ya marcado)
- [ ] Vista QR en web para el creador

---

## Fase 5 — Módulo Secretaría

**Objetivo**: Herramientas completas para Secretaría.

**Pantallas**:
- Dashboard Secretaría
- Registro de todas las reuniones
- Detalle con asistencia
- Fichas técnicas (crear, editar, finalizar)
- Calendario institucional
- Feriados y días no laborables
- Eventos institucionales
- Reportes Excel
- Logs funcionales

**Entregables**:
- [ ] Layout base Secretaría con identidad Ecuamatriz
- [ ] Todas las pantallas de secretaría funcionales
- [ ] Exportación Excel con openpyxl (reuniones, asistencia, fichas)
- [ ] Módulo de fichas técnicas completo
- [ ] Tests de reportes y fichas

---

## Fase 6 — Módulo Administrador completo

**Objetivo**: Panel de administración funcional.

**Pantallas**:
- Dashboard Admin
- CRUD usuarios completo
- CRUD áreas
- CRUD salas
- Configuración horario laboral
- Límites del sistema
- Configuración QR
- Configuración notificaciones
- Logs de auditoría

**Entregables**:
- [ ] Layout base Admin
- [ ] Todas las pantallas de Admin funcionales
- [ ] Formularios de configuración con validación
- [ ] Logs de auditoría paginados

---

## Fase 7 — App Android

**Objetivo**: App Android funcional para usuarios y secretaría.

**Pantallas**: Ver `docs/07_pantallas_android.md`

**Entregables**:
- [ ] Proyecto Android creado (Kotlin + Jetpack Compose)
- [ ] Configuración de servidor editable
- [ ] Login funcional con JWT
- [ ] Dashboard, reuniones, invitaciones
- [ ] Escaneo QR funcional
- [ ] Mostrar QR si es creador
- [ ] Notificaciones FCM
- [ ] Ficha técnica básica
- [ ] Pantallas básicas de Secretaría

---

## Fase 8 — Grabación y Transcripción

**Objetivo**: Integrar el módulo de audio del compañero externo.

**Prerequisito**: Recibir y revisar el código externo de grabación/transcripción.

**Entregables**:
- [ ] Integrar `MeetingRecording` + `RecordingStorageService`
- [ ] Integrar `MeetingTranscript` + `TranscriptionProvider`
- [ ] Generar `TechnicalSheetDraft` desde transcripción
- [ ] UI de revisión y aprobación de borrador
- [ ] Pantalla de grabación en Android (si es creador)
- [ ] Tests del flujo completo grabación → transcripción → borrador → ficha

---

## Criterios de aceptación por fase

Antes de cerrar una fase:
1. Todos los tests de la fase pasan sin errores.
2. No hay secretos en el código.
3. No hay código muerto ni placeholders sin documentar.
4. La bitácora (`docs/13_bitacora_avances.md`) está actualizada.
5. Las migraciones están al día.
6. El README está actualizado si aplica.

---

*Plan de fases — Fase 0 — Agenda Ecuamatriz*
