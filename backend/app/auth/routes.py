"""
app/auth/routes.py — ATENCIÓN: este archivo ya no registra el blueprint principal.
Agenda Ecuamatriz

El módulo auth fue dividido en dos blueprints separados (Cierre Fase 0):

    session_routes.py → auth_web_bp  → /auth/   (Flask-Login, web Jinja2)
    api_routes.py     → auth_api_bp  → /api/auth/ (JWT, Android)

Ambos están registrados en app/__init__.py → _register_blueprints().
Este archivo se mantiene solo para que imports históricos no rompan.
"""

# Los blueprints están en:
#   app.auth.session_routes → auth_web_bp
#   app.auth.api_routes     → auth_api_bp
