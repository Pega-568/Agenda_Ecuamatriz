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

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from app import csrf

auth_api_bp = Blueprint("auth_api", __name__)
csrf.exempt(auth_api_bp)


@auth_api_bp.route("/login", methods=["POST"])
def api_login():
    """
    POST /api/auth/login
    Autentica con email/contraseña.
    Retorna access_token y refresh_token (JWT).

    Body: { "email": "...", "password": "..." }
    Response: { "success": true, "data": { "access_token": "...", "refresh_token": "...", "user": {...} } }

    Implementado en Fase 1 para pruebas de API, separado del login web.
    """
    from app.auth.service import AuthService
    from app.shared.responses import error_response, success_response
    from app.users.service import UserService

    payload = request.get_json(silent=True) or {}
    user = AuthService.authenticate(payload.get("email", ""), payload.get("password", ""))
    if not user:
        return error_response("Credenciales inválidas o usuario inactivo.", 401, "INVALID_CREDENTIALS")
        
    from app.roles.models import RoleSlug
    if user.role.slug == RoleSlug.ADMIN:
        return error_response("El rol Administrador debe usar el panel web administrativo.", 403, "FORBIDDEN_ROLE")
        
    identity = str(user.id)
    return success_response(
        data={
            "access_token": create_access_token(identity=identity),
            "refresh_token": create_refresh_token(identity=identity),
            "user": UserService.to_dict(user),
        }
    )


@auth_api_bp.route("/logout", methods=["POST"])
@jwt_required(optional=True)
def api_logout():
    """
    POST /api/auth/logout
    Revoca el token JWT actual y desvincula el dispositivo móvil.
    """
    from app.shared.responses import success_response
    # Por simplicidad de diseño (Fase 6), confiamos en que la app móvil elimine su token.
    # TODO: Podría añadirse un TokenBlocklist aquí si es necesario más seguridad.
    return success_response(message="Sesión móvil cerrada exitosamente.")


@auth_api_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def api_refresh():
    """
    POST /api/auth/refresh
    Usa refresh_token para obtener nuevo access_token.
    """
    from app.shared.responses import success_response
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return success_response(data={"access_token": new_access_token})


@auth_api_bp.route("/me", methods=["GET"])
@jwt_required()
def api_me():
    """
    GET /api/auth/me
    Retorna datos del usuario autenticado (JWT).

    Implementado en Fase 1.
    """
    from app.shared.responses import error_response, success_response
    from app.users.service import UserService

    user = UserService.get_by_id(get_jwt_identity())
    if not user:
        return error_response("Usuario no encontrado.", 404, "USER_NOT_FOUND")
    return success_response(data=UserService.to_dict(user))

@auth_api_bp.route("/devices/register", methods=["POST"])
@jwt_required()
def api_register_device():
    """
    POST /api/auth/devices/register
    Registra un token FCM para el usuario autenticado.
    Body: {"fcm_token": "..."}
    """
    from app.shared.responses import error_response, success_response
    from app.users.models import MobileDeviceToken
    from app import db
    from datetime import datetime, timezone
    
    payload = request.get_json(silent=True) or {}
    fcm_token = payload.get("fcm_token")
    if not fcm_token:
        return error_response("El token FCM es requerido.", 400)
        
    user_id = int(get_jwt_identity())
    
    # Buscar si existe
    device = MobileDeviceToken.query.filter_by(fcm_token=fcm_token).first()
    if device:
        if device.user_id != user_id:
            device.user_id = user_id
        device.is_active = True
        device.last_used_at = datetime.now(timezone.utc)
    else:
        device = MobileDeviceToken(user_id=user_id, fcm_token=fcm_token)
        db.session.add(device)
        
    db.session.commit()
    return success_response(message="Dispositivo registrado exitosamente.")

@auth_api_bp.route("/devices/unregister", methods=["POST"])
@jwt_required()
def api_unregister_device():
    """
    POST /api/auth/devices/unregister
    Desvincula un token FCM.
    Body: {"fcm_token": "..."}
    """
    from app.shared.responses import error_response, success_response
    from app.users.models import MobileDeviceToken
    from app import db
    
    payload = request.get_json(silent=True) or {}
    fcm_token = payload.get("fcm_token")
    if not fcm_token:
        return error_response("El token FCM es requerido.", 400)
        
    user_id = int(get_jwt_identity())
    device = MobileDeviceToken.query.filter_by(fcm_token=fcm_token, user_id=user_id).first()
    
    if device:
        device.is_active = False
        db.session.commit()
        
    return success_response(message="Dispositivo desvinculado exitosamente.")
