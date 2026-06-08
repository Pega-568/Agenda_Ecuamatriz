# Agenda Ecuamatriz

Sistema interno de gestión de reuniones empresariales para **Ecuamatriz**.

---

## Estado del proyecto

| Fase | Descripción                                      | Estado        |
|------|--------------------------------------------------|---------------|
| 0    | Estructura, documentación y configuración base   | ✅ Completada  |
| 1    | Backend base (auth, users, roles, áreas, salas)  | 🔲 Pendiente   |
| 2    | Módulo reuniones, invitaciones, notificaciones   | 🔲 Pendiente   |
| 3    | Web Usuario                                      | 🔲 Pendiente   |
| 4    | QR de asistencia                                 | 🔲 Pendiente   |
| 5    | Módulo Secretaría                                | 🔲 Pendiente   |
| 6    | Módulo Administrador completo                    | 🔲 Pendiente   |
| 7    | App Android                                      | 🔲 Pendiente   |
| 8    | Grabación y transcripción de audio               | 🔲 Pendiente   |

---

## Descripción general

Agenda Ecuamatriz es una plataforma que permite:

- Crear y gestionar reuniones empresariales con un flujo único y estructurado.
- Buscar participantes y verificar su disponibilidad en tiempo real.
- Enviar invitaciones y registrar aceptaciones o rechazos.
- Gestionar salas, horarios laborales y calendario institucional.
- Marcar asistencia mediante código QR fijo por reunión.
- Generar fichas técnicas y actas de reunión.
- Exportar reportes a Excel.
- Enviar notificaciones web y móviles.
- (Futuro) Grabar y transcribir reuniones para generar borradores de fichas técnicas.

Consultar [`docs/00_vision_general.md`](docs/00_vision_general.md) para la visión completa del sistema.

---

## Tecnologías

| Capa        | Tecnología                                                       |
|-------------|------------------------------------------------------------------|
| Backend     | Python 3.11+, Flask, SQLAlchemy, Alembic, PostgreSQL             |
| Web         | Flask + Jinja2, CSS con identidad Ecuamatriz, Bootstrap (controlado) |
| Android     | Kotlin, Jetpack Compose, Retrofit, FCM, CameraX/ZXing            |
| Base de datos | PostgreSQL con migraciones Alembic                             |
| Notificaciones | Web (campana + centro), Android (FCM push)                   |
| QR          | Biblioteca `qrcode` Python, lectura con CameraX/ML Kit en Android |
| Reportes    | `openpyxl`                                                       |

---

## Estructura del proyecto

```
Agenda_Ecuamatriz/
├── backend/                  # API Flask + lógica de negocio
│   ├── app/
│   │   ├── auth/             # Autenticación JWT, login, logout
│   │   ├── users/            # CRUD usuarios, perfiles
│   │   ├── roles/            # Roles: admin, secretary, user
│   │   ├── areas/            # Áreas de la empresa
│   │   ├── rooms/            # Salas de reunión
│   │   ├── settings/         # Configuración del sistema
│   │   ├── calendar/         # Calendario laboral, feriados
│   │   ├── meetings/         # Reuniones: crear, gestionar
│   │   ├── availability/     # Validación de disponibilidad
│   │   ├── attendance/       # QR, marcado de asistencia
│   │   ├── notifications/    # Notificaciones web y FCM
│   │   ├── technical_sheets/ # Fichas técnicas / actas
│   │   ├── reports/          # Exportación Excel
│   │   ├── audit/            # Logs de auditoría
│   │   ├── recordings/       # (Fase 8) Grabaciones
│   │   ├── transcriptions/   # (Fase 8) Transcripciones
│   │   └── shared/           # Utilidades, decoradores, respuestas comunes
│   ├── migrations/           # Migraciones Alembic / Flask-Migrate
│   ├── tests/                # Tests con pytest
│   ├── scripts/              # Seeders y scripts de utilidad
│   ├── run.py                # Punto de entrada de la aplicación
│   └── requirements.txt      # Dependencias Python
├── web/                      # Plantillas Jinja2 y assets estáticos
│   ├── static/               # CSS, JS, imágenes
│   └── templates/            # Vistas HTML por módulo
├── android/                  # App Android Kotlin (Fase 7)
├── docs/                     # Documentación técnica completa
├── .env.example              # Plantilla de variables de entorno
├── .gitignore
└── README.md
```

---

## Requisitos previos

- Python 3.11 o superior
- PostgreSQL 14 o superior
- Git

---

## Configuración inicial del entorno

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd Agenda_Ecuamatriz

# 2. Crear entorno virtual
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp ../.env.example ../.env
# Editar .env con los valores reales

# 5. Crear base de datos en PostgreSQL
# Conectarse a psql y ejecutar:
# CREATE DATABASE agenda_ecuamatriz;

# 6. Ejecutar migraciones
flask db upgrade

# 7. Ejecutar seeders
python scripts/seed_all.py

# 8. Iniciar servidor de desarrollo
python run.py
```

---

## Roles del sistema

| Rol          | Descripción                                                                                      |
|--------------|--------------------------------------------------------------------------------------------------|
| Administrador | Gestión técnica: usuarios, áreas, salas, parámetros del sistema. No participa en reuniones.    |
| Secretaría   | Registro, seguimiento, fichas técnicas, reportes, calendario institucional.                      |
| Usuario      | Crea reuniones, invita participantes, acepta/rechaza, marca asistencia, completa fichas técnicas. |

---

## Documentación

| Documento                              | Contenido                                          |
|----------------------------------------|----------------------------------------------------|
| [00_vision_general.md](docs/00_vision_general.md)       | Visión, objetivos y principios del sistema |
| [01_roles_permisos.md](docs/01_roles_permisos.md)       | Roles, permisos y restricciones detalladas |
| [02_flujo_nueva_reunion.md](docs/02_flujo_nueva_reunion.md) | Flujo completo de creación de reunión   |
| [03_modelo_datos.md](docs/03_modelo_datos.md)           | Entidades, campos y relaciones             |
| [04_contrato_api.md](docs/04_contrato_api.md)           | Endpoints, contratos JSON, códigos HTTP    |
| [05_guia_visual_ecuamatriz.md](docs/05_guia_visual_ecuamatriz.md) | Paleta, tipografía, componentes  |
| [06_pantallas_web.md](docs/06_pantallas_web.md)         | Listado y descripción de pantallas web     |
| [07_pantallas_android.md](docs/07_pantallas_android.md) | Pantallas de la app Android                |
| [08_notificaciones.md](docs/08_notificaciones.md)       | Tipos, canales y reglas de notificación    |
| [09_qr_asistencia.md](docs/09_qr_asistencia.md)         | Generación, validación y ventana QR        |
| [10_ficha_tecnica_audio.md](docs/10_ficha_tecnica_audio.md) | Fichas técnicas y módulo futuro audio  |
| [11_plan_fases.md](docs/11_plan_fases.md)               | Plan de fases y entregables por fase       |
| [12_normas_codigo.md](docs/12_normas_codigo.md)         | Normas de código, arquitectura, pruebas    |
| [13_bitacora_avances.md](docs/13_bitacora_avances.md)   | Bitácora cronológica de avances            |

---

## Identidad visual

El sistema usa la paleta corporativa de Ecuamatriz:

| Nombre             | Hex       |
|--------------------|-----------|
| Electric Blue      | `#003091` |
| Blue Lightning     | `#0057FF` |
| Celeste corporativo| `#48C9E3` |
| Gris claro         | `#F3F3F3` |
| Gris medio         | `#C0C0C0` |
| Gris oscuro        | `#4D4D4D` |
| Blanco             | `#FFFFFF` |

Fuente principal del sistema: **Lato** (con fallback a Inter).

---

## Normas esenciales

- No commitear `.env` ni archivos con secretos.
- No subir APKs, ZIPs pesados, carpetas `venv/`, `node_modules/`, `dist/`.
- Cada módulo tiene responsabilidad única y separación de capas.
- Toda acción crítica registra auditoría.
- Toda regla de negocio tiene al menos un test.
- Consultar [`docs/12_normas_codigo.md`](docs/12_normas_codigo.md) antes de contribuir.

---

## Contribución

Este es un sistema interno de Ecuamatriz. El acceso al repositorio está restringido al equipo de desarrollo autorizado.

---

*Proyecto reiniciado desde cero — Fase 0 completada el 2026-06-07*
