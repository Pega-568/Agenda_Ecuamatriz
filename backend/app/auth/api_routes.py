"""
app/auth/api_routes.py — Rutas de autenticación API (JWT para Android)
Agenda Ecuamatriz

Canal: Endpoints JSON en /api/auth/
Mecanismo: Flask-JWT-Extended — access token + refresh token

Endpoints:
    POST /api/auth/login    — Autenticar, retornar access + refresh token
    POST /api/auth/logout   — Revocar token (blocklist en BD o Redis futuro)
    POST /api/auth/refresh  — Obtener nuevo access_token con refresh_token
    GET  /api/auth/me       — Perfil del usuario autenticado (JWT)

Reglas:
    - Solo para la app Android (Fase 7+).
    - NO usar en vistas Jinja2.
    - El token se incluye en header: Authorization: Bearer <token>
    - Decoradores: @jwt_required() para rutas protegidas.

Fase de implementación: Fase 7 (Android)
Fase 1 puede implementar /login y /me para pruebas de API aunque la app Android no esté.
"""

from flask import Blueprint

auth_api_bp = Blueprint("auth_api", __name__)


@auth_api_bp.route("/login", methods=["POST"])
def api_login():
    """
    POST /api/auth/login
    Autentica con email/contraseña.
    Retorna access_token y refresh_token (JWT).

    Body: { "email": "...", "password": "..." }
    Response: { "success": true, "data": { "access_token": "...", "refresh_token": "...", "user": {...} } }

    TODO (Fase 1): Implementar AuthService.authenticate() + create_access_token()
    """
    from app.shared.responses import error_response
    return error_response("API login JWT — implementación pendiente (Fase 1).", 501)


@auth_api_bp.route("/logout", methods=["POST"])
def api_logout():
    """
    POST /api/auth/logout
    Revoca el token JWT actual.

    TODO (Fase 7): Implementar blocklist con @jwt_required()
    """
    from app.shared.responses import error_response
    return error_response("API logout JWT — implementación pendiente (Fase 7).", 501)


@auth_api_bp.route("/refresh", methods=["POST"])
def api_refresh():
    """
    POST /api/auth/refresh
    Usa refresh_token para obtener nuevo access_token.

    TODO (Fase 7): Implementar con @jwt_required(refresh=True)
    """
    from app.shared.responses import error_response
    return error_response("API refresh JWT — implementación pendiente (Fase 7).", 501)


@auth_api_bp.route("/me", methods=["GET"])
def api_me():
    """
    GET /api/auth/me
    Retorna datos del usuario autenticado (JWT).

    TODO (Fase 1): Implementar con @jwt_required()
    """
    from app.shared.responses import error_response
    return error_response("API me JWT — implementación pendiente (Fase 1).", 501)
