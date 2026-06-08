# 00 — Visión General del Sistema

## Agenda Ecuamatriz

### ¿Qué es?

Agenda Ecuamatriz es una plataforma interna de gestión de reuniones empresariales para **Ecuamatriz**. Permite planificar, convocar, confirmar, realizar y documentar reuniones de forma eficiente, controlada y auditable.

---

### Contexto y motivación

El prototipo anterior del sistema quedó fragmentado: múltiples ramas inconsistentes, lógica duplicada entre backend, web y Android, pantallas no conectadas, y deuda técnica acumulada. Este nuevo sistema se construye **desde cero**, de forma limpia, modular y documentada.

El sistema anterior sirve únicamente como **referencia funcional** — para entender qué debe funcionar — no como base de código.

---

### Objetivo del sistema

Crear una plataforma interna que permita:

1. **Crear reuniones** con un flujo único, estructurado y validado.
2. **Buscar participantes** dentro de la empresa.
3. **Ver disponibilidad** integrada en el flujo de creación (no en pantalla separada).
4. **Enviar invitaciones** y registrar aceptaciones/rechazos.
5. **Gestionar salas** con verificación de disponibilidad.
6. **Bloquear reuniones** fuera de horarios laborales o días no laborables.
7. **Marcar asistencia** mediante QR fijo por reunión.
8. **Generar fichas técnicas / actas** de reunión.
9. **Exportar reportes** a Excel.
10. **Gestionar notificaciones** web y móviles.
11. *(Futuro)* **Grabar y transcribir** reuniones para generar borradores de fichas técnicas.

---

### Principio central — Flujo único de reunión

**No existen tipos de reunión.** No hay reunión institucional, reunión interna, reunión de área, etc. Hay un solo flujo:

```
Nueva reunión
  → Datos generales (título, objetivo, descripción)
  → Orden del día (obligatorio, estructurado)
  → Fecha / hora inicio / hora fin
  → Sala o modalidad virtual
  → Búsqueda de participantes
  → Disponibilidad integrada (en el mismo flujo)
  → Confirmación y creación
  → Invitación automática a participantes
  → Aceptación / rechazo por cada invitado
  → Reunión se realiza
  → Asistencia marcada por QR
  → Ficha técnica completada por el creador
```

---

### Regla principal de convocatoria

- **Cualquier usuario puede convocar reuniones.**
- Los invitados conservan el derecho de **aceptar o rechazar**.
- El sistema valida disponibilidad, sala, horarios y calendario **antes de permitir la creación**.
- La reunión bloquea la agenda del **creador automáticamente**.
- Para los invitados, bloquea la agenda solo si **aceptan**.

---

### Stack tecnológico

| Capa             | Tecnología                                              |
|------------------|---------------------------------------------------------|
| Backend API      | Python 3.11+, Flask, SQLAlchemy, Alembic, PostgreSQL    |
| Web              | Flask + Jinja2, CSS Ecuamatriz, Bootstrap (controlado)  |
| Android          | Kotlin, Jetpack Compose, Retrofit, FCM, CameraX         |
| Base de datos    | PostgreSQL con migraciones Alembic                      |
| QR               | `qrcode` (Python), CameraX/ML Kit (Android)             |
| Reportes         | `openpyxl`                                              |
| Notificaciones   | Web: sistema interno, Android: FCM                      |

---

### Fases de construcción

| Fase | Alcance                                        |
|------|------------------------------------------------|
| 0    | Estructura, documentación, configuración base  |
| 1    | Backend base (auth, users, roles, áreas, salas)|
| 2    | Módulo reuniones + invitaciones + notificaciones|
| 3    | Web Usuario                                    |
| 4    | QR de asistencia                               |
| 5    | Módulo Secretaría                              |
| 6    | Módulo Administrador completo                  |
| 7    | App Android                                    |
| 8    | Grabación y transcripción (módulo externo)     |

---

### Premisas de arquitectura

- **No mezclar lógica de negocio con vistas.** Nunca.
- **No duplicar lógica entre web y API.** La web consume la misma API que Android.
- **Blueprints por módulo.** Cada módulo es independiente.
- **Servicios para lógica de negocio.** Las rutas solo orquestan, los servicios ejecutan.
- **Toda acción crítica registra auditoría.**
- **Toda regla de negocio tiene al menos un test.**
- **Migraciones controladas.** Nunca modificar la BD directamente.

---

*Documento de visión — Fase 0 — Agenda Ecuamatriz*
