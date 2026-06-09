# Web Operativa (Fase 5)

## Visión General
Este documento detalla la estructura implementada en la **Fase 5** del proyecto, orientada a construir la interfaz web operativa del sistema Agenda Ecuamatriz utilizando Jinja2, separada por completo del front-end en la antigua versión que intentaba ser una SPA o un cliente separado.

## Arquitectura de Vistas (Jinja2)
Las vistas del sistema se gestionan a través de la carpeta `web/templates` y el módulo Python correspondiente `app/web`.
Hemos descartado Single Page Applications (React, Angular) en favor de plantillas renderizadas desde el servidor.

1. **Módulo de Blueprints**:
   - `web_admin_bp` en `admin_routes.py`: Gestión global.
   - `web_user_bp` en `user_routes.py`: Gestión personal y de reuniones.
   - `web_secretary_bp` en `secretary_routes.py`: Consola de control de todas las reuniones institucionales.

2. **Templates Jinja2**:
   - **`layouts/`**: `base.html` y `auth.html` para la estructura general del sitio.
   - **`partials/`**: Elementos repetitivos (`sidebar.html`, `topbar.html`, `flashes.html`).
   - Componentes individuales de cada módulo según el usuario final.

## Identidad Corporativa y CSS
Todo el diseño se maneja en **Vanilla CSS** con variables modulares y clases semánticas, siguiendo la paleta de colores de Ecuamatriz:
- Primario: `#003091`
- Secundario: `#0057FF`
- Acento: `#48C9E3`

La estructura modular incluye:
- `app.css`: Reset y variables principales (colores, fuentes y tipografía, espaciados y sombras).
- `layout.css`: Contenedores principales (grid corporativo).
- `components.css`: Clases como `.card`, `.btn`, `.table`, `.badge`.
- `forms.css`: Formularios y estructura interactiva.

## Seguridad Web
Se implementó `WTF_CSRF_ENABLED` para todos los formularios. 
Las rutas están resguardadas detrás del decorador `@login_required` de **Flask-Login** con redirección controlada por rol. Todo el sistema requiere una sesión válida generada por `/auth/login` (session cookie del lado del servidor).
