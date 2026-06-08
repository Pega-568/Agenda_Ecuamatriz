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

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

auth_web_bp = Blueprint("auth_web", __name__)


@auth_web_bp.route("/login", methods=["GET"])
def login_form():
    """
    GET /auth/login
    Muestra el formulario de login.
    Si el usuario ya está autenticado, redirige a su dashboard.

    Implementado en Fase 1.
    """
    if current_user.is_authenticated:
        return redirect(url_for("auth_web.dashboard"))
    return render_template("auth/login.html", error=None)


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

    Implementado en Fase 1.
    """
    from app.auth.service import AuthService

    email = request.form.get("email", "")
    password = request.form.get("password", "")
    user = AuthService.authenticate(email, password)
    if not user:
        return render_template("auth/login.html", error="Credenciales inválidas o usuario inactivo."), 401
    login_user(user)
    return redirect(url_for("auth_web.dashboard"))


@auth_web_bp.route("/logout")
def logout():
    """
    GET /auth/logout
    Cierra la sesión del usuario actual.
    Llama a logout_user() de Flask-Login y redirige a /auth/login.

    Implementado en Fase 1.
    """
    logout_user()
    return redirect(url_for("auth_web.login_form"))


@auth_web_bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard mínimo por rol para validar sesión web."""
    return render_template("dashboard.html")
