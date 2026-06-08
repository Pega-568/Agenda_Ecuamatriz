"""
app/auth/session_routes.py — Rutas de autenticación WEB (Flask-Login)
Agenda Ecuamatriz

Canal: Vistas Jinja2 en /auth/
Mecanismo: Flask-Login + sesiones servidor + cookies seguras + CSRF

Endpoints:
    GET  /auth/login   — Formulario de login
    POST /auth/login   — Procesar login, crear sesión
    GET  /auth/logout  — Cerrar sesión

Reglas:
    - NO retornar JWT aquí.
    - NO guardar token en localStorage.
    - La sesión se mantiene en el servidor (cookie firma con SECRET_KEY).
    - Los formularios tienen protección CSRF via Flask-WTF.

Fase de implementación: Fase 1
"""

from flask import Blueprint

auth_web_bp = Blueprint("auth_web", __name__)


@auth_web_bp.route("/login", methods=["GET"])
def login_form():
    """
    GET /auth/login
    Muestra el formulario de login.
    Si el usuario ya está autenticado, redirige a su dashboard.

    TODO (Fase 1): Implementar con render_template("auth/login.html")
    """
    from app.shared.responses import error_response
    return error_response("Vista de login web — implementación pendiente (Fase 1).", 501)


@auth_web_bp.route("/login", methods=["POST"])
def login_submit():
    """
    POST /auth/login
    Procesa el formulario de login.
    Si las credenciales son válidas:
        - Llama a login_user(user) de Flask-Login.
        - Redirige al dashboard según el rol.
    Si son inválidas:
        - Vuelve al formulario con mensaje de error.

    TODO (Fase 1): Implementar con AuthService.authenticate() + login_user()
    """
    from app.shared.responses import error_response
    return error_response("Login web — implementación pendiente (Fase 1).", 501)


@auth_web_bp.route("/logout")
def logout():
    """
    GET /auth/logout
    Cierra la sesión del usuario actual.
    Llama a logout_user() de Flask-Login y redirige a /auth/login.

    TODO (Fase 1): Implementar con logout_user() + redirect
    """
    from app.shared.responses import error_response
    return error_response("Logout web — implementación pendiente (Fase 1).", 501)
