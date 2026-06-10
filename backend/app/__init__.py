"""
app/__init__.py — Application Factory
Agenda Ecuamatriz

Patrón: Application Factory de Flask.
Permite instanciar la app múltiples veces con configuraciones distintas
(producción, testing, development) sin efectos secundarios globales.

Decisiones de autenticación (Cierre Fase 0):
    WEB (Jinja2):   Flask-Login con sesiones servidor + cookies seguras + CSRF
    API MÓVIL:      Flask-JWT-Extended para endpoints /api/ (Android, Fase 7+)
    Regla:          NO usar JWT en la web. NO guardar JWT en localStorage.
                    La separación se hace por blueprint: /web/ vs /api/
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

# ─── Extensiones (instanciadas aquí, inicializadas en create_app) ───────────
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()
csrf = CSRFProtect()


def create_app(config_object=None):
    """
    Crea y configura la aplicación Flask.

    Args:
        config_object: Objeto de configuración opcional.
                       Si es None, se carga desde variables de entorno.
                       Usar TestConfig en tests.

    Returns:
        Flask app configurada y lista para ejecutar.
    """
    app = Flask(
        __name__,
        template_folder="../../web/templates",
        static_folder="../../web/static",
    )

    # ─── Configuración ────────────────────────────────────────────────────
    _configure_app(app, config_object)

    # ─── Inicializar extensiones ──────────────────────────────────────────
    db.init_app(app)
    _register_models()
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)

    # Flask-Login — autenticación web con sesiones servidor
    login_manager.init_app(app)
    login_manager.login_view = "auth_web.login_form"
    login_manager.login_message = "Inicia sesión para acceder."
    login_manager.login_message_category = "warning"

    # Flask-JWT-Extended — autenticación API para app Android
    jwt.init_app(app)

    # CSRF — protección para formularios Jinja2
    # Siempre se inicializa para inyectar csrf_token() en Jinja2.
    # Flask-WTF respeta WTF_CSRF_ENABLED para saltar validación en tests.
    csrf.init_app(app)

    # CORS — solo para endpoints /api/ consumidos por Android
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", [])}},
    )

    # ─── Registrar blueprints ─────────────────────────────────────────────
    _register_blueprints(app)

    # ─── Endpoint /health ─────────────────────────────────────────────────
    _register_health_endpoint(app)

    # ─── Endpoint raíz / ──────────────────────────────────────────────────
    @app.route("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("auth_web.login_form"))

    # ─── Registrar manejadores de error globales ──────────────────────────
    _register_error_handlers(app)

    return app


def _register_models():
    """
    Importa todos los modelos para registrar clases y tablas en SQLAlchemy.

    Las relaciones usan nombres de clase en string para evitar imports circulares,
    pero SQLAlchemy necesita que esas clases hayan sido importadas antes de
    configurar mappers, ejecutar tests con create_all() o generar migraciones.
    """
    from app.areas import models as _areas_models  # noqa: F401
    from app.attendance import models as _attendance_models  # noqa: F401
    from app.audit import models as _audit_models  # noqa: F401
    from app.calendar import models as _calendar_models  # noqa: F401
    from app.meetings import models as _meetings_models  # noqa: F401
    from app.notifications import models as _notifications_models  # noqa: F401
    from app.recordings import models as _recordings_models  # noqa: F401
    from app.roles import models as _roles_models  # noqa: F401
    from app.rooms import models as _rooms_models  # noqa: F401
    from app.settings import models as _settings_models  # noqa: F401
    from app.technical_sheets import models as _technical_sheets_models  # noqa: F401
    from app.transcriptions import models as _transcriptions_models  # noqa: F401
    from app.users import models as _users_models  # noqa: F401


def _configure_app(app: Flask, config_object=None):
    """Carga la configuración desde el objeto dado o desde variables de entorno."""
    import os
    from datetime import timedelta

    if config_object:
        app.config.from_object(config_object)
        return

    # DATABASE_URL debe usar postgresql+psycopg:// (psycopg v3)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL no configurada. "
            "Copia .env.example a .env y configura la URL de PostgreSQL."
        )

    app.config.update(
        # ─── Flask ───────────────────────────────────────────────────────
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-insecure-key-CAMBIAR"),
        TESTING=False,
        DEBUG=os.getenv("FLASK_DEBUG", "0") == "1",

        # ─── Base de datos ────────────────────────────────────────────────
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_pre_ping": True,   # Detectar conexiones caídas
            "pool_recycle": 3600,    # Reciclar conexiones cada hora
        },

        # ─── Sesiones web (Flask-Login) ───────────────────────────────────
        SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "False") == "True",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE=os.getenv("SESSION_COOKIE_SAMESITE", "Lax"),
        PERMANENT_SESSION_LIFETIME=timedelta(
            seconds=int(os.getenv("PERMANENT_SESSION_LIFETIME", 28800))
        ),

        # ─── JWT (API móvil Android) ──────────────────────────────────────
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "dev-jwt-insecure-key-CAMBIAR"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(
            minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 60))
        ),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(
            days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 7))
        ),

        # ─── CSRF ─────────────────────────────────────────────────────────
        WTF_CSRF_ENABLED=os.getenv("WTF_CSRF_ENABLED", "True") == "True",

        # ─── Correo ───────────────────────────────────────────────────────
        MAIL_ENABLED=os.getenv("MAIL_ENABLED", "False") == "True",
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True") == "True",
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
        MAIL_SUPPRESS_SEND=os.getenv("FLASK_ENV") != "production",

        # ─── FCM ─────────────────────────────────────────────────────────
        FCM_ENABLED=os.getenv("FCM_ENABLED", "False") == "True",

        # ─── CORS ─────────────────────────────────────────────────────────
        CORS_ORIGINS=os.getenv("CORS_ORIGINS", "").split(","),

        # ─── Aplicación ───────────────────────────────────────────────────
        APP_NAME=os.getenv("APP_NAME", "Agenda Ecuamatriz"),
        APP_URL=os.getenv("APP_URL", "http://localhost:5000"),

        # ─── QR ───────────────────────────────────────────────────────────
        QR_OUTPUT_DIR=os.getenv("QR_OUTPUT_DIR", "app/attendance/generated_qr"),
        QR_DEFAULT_VALID_BEFORE_MINUTES=int(
            os.getenv("QR_DEFAULT_VALID_BEFORE_MINUTES", 15)
        ),
        QR_DEFAULT_VALID_AFTER_MINUTES=int(
            os.getenv("QR_DEFAULT_VALID_AFTER_MINUTES", 30)
        ),

        # ─── Reportes ─────────────────────────────────────────────────────
        REPORTS_OUTPUT_DIR=os.getenv("REPORTS_OUTPUT_DIR", "app/reports/exports"),
    )


# ─── User loader para Flask-Login ───────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id: str):
    """
    Callback requerido por Flask-Login.
    Carga el usuario desde la BD a partir del ID en la sesión.
    El modelo User debe implementar la interfaz UserMixin.
    """
    from app.users.models import User
    return db.session.get(User, int(user_id))


def _register_blueprints(app: Flask):
    """
    Registra todos los blueprints de la aplicación.

    Separación de canales:
        /web/  → Vistas Jinja2 con Flask-Login (sesiones)
        /api/  → Endpoints JSON para Android con JWT (Fase 7+)

    En Fases 0-6, los endpoints /api/ existen como stubs.
    Las vistas /web/ se implementan en Fase 3.
    """
    # ─── Auth — sesión web ────────────────────────────────────────────────
    from app.auth.session_routes import auth_web_bp
    app.register_blueprint(auth_web_bp, url_prefix="/auth")
    
    # ─── Vistas Web (Jinja2) ─────────────────────────────────────────────
    from app.web.admin_routes import web_admin_bp
    app.register_blueprint(web_admin_bp)
    
    from app.web.user_routes import web_user_bp
    app.register_blueprint(web_user_bp)
    
    from app.web.secretary_routes import web_secretary_bp
    app.register_blueprint(web_secretary_bp)

    from app.web.attendance_routes import web_attendance_bp
    app.register_blueprint(web_attendance_bp)

    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        if current_user.is_authenticated:
            from app.notifications.service import NotificationService
            static_notes = NotificationService.list_for_user(current_user.id)
            static_dicts = [NotificationService.to_dict(n) for n in static_notes if not n.is_read]
            dynamic_notes = NotificationService.get_dynamic_notifications(current_user)
            all_notes = static_dicts + dynamic_notes
            all_notes.sort(key=lambda x: x["created_at"], reverse=True)
            return dict(unread_notifications=all_notes)
        return dict(unread_notifications=[])

    # ─── Auth — API JWT para móvil ────────────────────────────────────────
    from app.auth.api_routes import auth_api_bp
    csrf.exempt(auth_api_bp)
    app.register_blueprint(auth_api_bp, url_prefix="/api/auth")

    # ─── Users ────────────────────────────────────────────────────────────
    from app.users.routes import users_bp
    csrf.exempt(users_bp)
    app.register_blueprint(users_bp, url_prefix="/api/users")

    # ─── Roles ────────────────────────────────────────────────────────────
    from app.roles.routes import roles_bp
    csrf.exempt(roles_bp)
    app.register_blueprint(roles_bp, url_prefix="/api/roles")

    # ─── Areas ────────────────────────────────────────────────────────────
    from app.areas.routes import areas_bp
    csrf.exempt(areas_bp)
    app.register_blueprint(areas_bp, url_prefix="/api/areas")

    # ─── Rooms ────────────────────────────────────────────────────────────
    from app.rooms.routes import rooms_bp
    csrf.exempt(rooms_bp)
    app.register_blueprint(rooms_bp, url_prefix="/api/rooms")

    # ─── System Settings ──────────────────────────────────────────────────
    from app.settings.routes import settings_bp
    csrf.exempt(settings_bp)
    app.register_blueprint(settings_bp, url_prefix="/api/settings")

    # ─── Work Calendar ────────────────────────────────────────────────────
    from app.calendar.routes import calendar_bp
    csrf.exempt(calendar_bp)
    app.register_blueprint(calendar_bp, url_prefix="/api/calendar")

    # ─── Meetings ─────────────────────────────────────────────────────────
    from app.meetings.routes import meetings_bp
    csrf.exempt(meetings_bp)
    app.register_blueprint(meetings_bp, url_prefix="/api/meetings")

    # ─── API Móvil Específica (Android Fase 7+) ───────────────────────────
    from app.api.mobile.meeting_routes import mobile_meetings_bp
    csrf.exempt(mobile_meetings_bp)
    app.register_blueprint(mobile_meetings_bp, url_prefix="/api/mobile/meetings")

    from app.api.mobile.attendance_routes import mobile_attendance_bp
    csrf.exempt(mobile_attendance_bp)
    app.register_blueprint(mobile_attendance_bp, url_prefix="/api/mobile/attendance")

    from app.api.mobile.notification_routes import mobile_notifications_bp
    csrf.exempt(mobile_notifications_bp)
    app.register_blueprint(mobile_notifications_bp, url_prefix="/api/mobile/notifications")

    # ─── Availability ─────────────────────────────────────────────────────
    from app.availability.routes import availability_bp
    csrf.exempt(availability_bp)
    app.register_blueprint(availability_bp, url_prefix="/api/availability")

    # ─── Attendance / QR ──────────────────────────────────────────────────
    from app.attendance.routes import attendance_bp
    csrf.exempt(attendance_bp)
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")

    # ─── Notifications ────────────────────────────────────────────────────
    from app.notifications.routes import notifications_bp
    csrf.exempt(notifications_bp)
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    # ─── Technical Sheets ─────────────────────────────────────────────────
    from app.technical_sheets.routes import technical_sheets_bp
    csrf.exempt(technical_sheets_bp)
    app.register_blueprint(technical_sheets_bp, url_prefix="/api/technical-sheets")

    # ─── Reports ──────────────────────────────────────────────────────────
    from app.reports.routes import reports_bp
    csrf.exempt(reports_bp)
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    # ─── Audit Logs ───────────────────────────────────────────────────────
    from app.audit.routes import audit_bp
    csrf.exempt(audit_bp)
    app.register_blueprint(audit_bp, url_prefix="/api/audit")

    # ─── Recordings (Fase 8 — módulo futuro) ─────────────────────────────
    from app.recordings.routes import recordings_bp
    csrf.exempt(recordings_bp)
    app.register_blueprint(recordings_bp, url_prefix="/api/recordings")

    # ─── Transcriptions (Fase 8 — módulo futuro) ─────────────────────────
    from app.transcriptions.routes import transcriptions_bp
    csrf.exempt(transcriptions_bp)
    app.register_blueprint(transcriptions_bp, url_prefix="/api/transcriptions")


def _register_health_endpoint(app: Flask):
    """
    Endpoint /health — verificación de estado del servidor.
    No requiere autenticación.
    Útil para healthchecks de Docker, balanceadores de carga y scripts de CI.
    """
    @app.route("/health")
    def health():
        """
        GET /health
        Verifica que el servidor está activo y puede conectar a la BD.
        """
        try:
            # Verificar conexión a PostgreSQL
            db.session.execute(db.text("SELECT 1"))
            db_status = "ok"
        except Exception as e:
            db_status = f"error: {str(e)}"

        status = "ok" if db_status == "ok" else "degraded"
        http_code = 200 if status == "ok" else 503

        return jsonify({
            "status": status,
            "app": app.config.get("APP_NAME", "Agenda Ecuamatriz"),
            "database": db_status,
        }), http_code


def _register_error_handlers(app: Flask):
    """Manejadores de error HTTP globales con respuesta JSON consistente."""
    from app.shared.responses import error_response

    @app.errorhandler(400)
    def bad_request(e):
        return error_response("Solicitud incorrecta.", 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return error_response("No autenticado.", 401)

    @app.errorhandler(403)
    def forbidden(e):
        return error_response("Acceso denegado.", 403)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("Recurso no encontrado.", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("Método no permitido.", 405)

    @app.errorhandler(422)
    def unprocessable(e):
        return error_response("Datos de entrada inválidos.", 422)

    @app.errorhandler(500)
    def internal_error(e):
        return error_response("Error interno del servidor.", 500)
