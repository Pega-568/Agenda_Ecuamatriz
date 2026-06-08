"""
tests/conftest.py — Configuración global de pytest
Agenda Ecuamatriz

DECISIÓN (Cierre Fase 0):
    Tests usan PostgreSQL real (Docker), NO SQLite.
    Razón: El sistema depende de fechas, constraints, JSON, transacciones
    y operaciones que SQLite puede comportar de forma distinta a PostgreSQL.

PREREQUISITO para ejecutar tests:
    1. Docker corriendo: docker compose up -d
    2. BD de test creada (se crea automáticamente vía docker/postgres/init.sql)
    3. TEST_DATABASE_URL en .env:
       postgresql+psycopg://agenda_user:agenda_password@127.0.0.1:5432/agenda_ecuamatriz_test

Fixtures disponibles:
    - app          : Instancia Flask apuntando a BD de test PostgreSQL
    - client       : Cliente HTTP de prueba
    - db_session   : Sesión BD con rollback por test (aislamiento)
    - admin_user   : Usuario admin de prueba
    - secretary_user: Usuario secretaría de prueba
    - regular_user : Usuario colaborador de prueba
    - auth_headers_admin / auth_headers_secretary / auth_headers_user
"""

import os
import pytest
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto (dos niveles arriba de tests/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from app import create_app, db as _db
from app.roles.models import Role, RoleSlug
from app.areas.models import Area
from app.users.models import User


def _get_test_db_url() -> str:
    """
    Obtiene la URL de la BD de test.
    Falla con mensaje claro si no está configurada.
    """
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        raise RuntimeError(
            "\n\n[ERROR] TEST_DATABASE_URL no está configurada.\n"
            "Pasos para configurar:\n"
            "  1. Asegúrate de que Docker está corriendo: docker compose up -d\n"
            "  2. Copia .env.example a .env y configura TEST_DATABASE_URL:\n"
            "     TEST_DATABASE_URL=postgresql+psycopg://agenda_user:agenda_password"
            "@127.0.0.1:5432/agenda_ecuamatriz_test\n"
        )
    if "sqlite" in url.lower():
        raise RuntimeError(
            "\n\n[ERROR] TEST_DATABASE_URL apunta a SQLite.\n"
            "Los tests de Agenda Ecuamatriz requieren PostgreSQL real.\n"
            "Configura TEST_DATABASE_URL con una URL de PostgreSQL.\n"
        )
    return url


class TestConfig:
    """
    Configuración Flask para entorno de tests.
    Usa PostgreSQL (Docker), no SQLite.
    """
    TESTING = True
    SECRET_KEY = "test-secret-key-no-usar-en-produccion"
    SQLALCHEMY_DATABASE_URI = None  # Se sobreescribe en fixture app()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # Flask-Login
    LOGIN_DISABLED = False
    WTF_CSRF_ENABLED = False        # Desactivar CSRF en tests

    # JWT
    JWT_SECRET_KEY = "test-jwt-secret-no-usar-en-produccion"
    JWT_ACCESS_TOKEN_EXPIRES = 3600

    # Mail
    MAIL_SUPPRESS_SEND = True
    MAIL_ENABLED = False

    # FCM
    FCM_ENABLED = False

    # QR y reportes — usar directorio temporal en tests
    QR_OUTPUT_DIR = "tests/tmp/qr"
    REPORTS_OUTPUT_DIR = "tests/tmp/reports"

    APP_NAME = "Agenda Ecuamatriz (Test)"
    APP_URL = "http://localhost:5000"
    CORS_ORIGINS = []
    QR_DEFAULT_VALID_BEFORE_MINUTES = 15
    QR_DEFAULT_VALID_AFTER_MINUTES = 30


@pytest.fixture(scope="session")
def app():
    """
    Crea la aplicación Flask apuntando a la BD de test PostgreSQL.

    Scope session: la app se crea una sola vez por sesión de tests.
    La BD se limpia al iniciar y al finalizar.
    """
    test_db_url = _get_test_db_url()
    TestConfig.SQLALCHEMY_DATABASE_URI = test_db_url

    flask_app = create_app(TestConfig)

    with flask_app.app_context():
        # Crear todas las tablas en la BD de test
        # En ambiente real se usa flask db upgrade.
        # En tests usamos create_all() sobre la BD de test para rapidez.
        _db.create_all()
        _seed_test_roles_and_areas()
        yield flask_app
        # Limpiar al finalizar la sesión
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    """Cliente HTTP de prueba Flask."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """
    Sesión de BD con rollback automático al finalizar cada test.
    Garantiza aislamiento: cada test trabaja en una transacción que se revierte.

    Nota: Funciona con PostgreSQL. En SQLite el comportamiento puede diferir.
    """
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()

        # Configurar la sesión para usar la conexión con transacción abierta
        _db.session.configure(bind=connection)

        yield _db.session

        _db.session.remove()
        transaction.rollback()
        connection.close()


# ─── Datos base de test ──────────────────────────────────────────────────────

def _seed_test_roles_and_areas():
    """Inserta roles y área de prueba. Idempotente."""
    for slug, name in [
        (RoleSlug.ADMIN, "Administrador"),
        (RoleSlug.SECRETARY, "Secretaría"),
        (RoleSlug.USER, "Usuario"),
    ]:
        if not Role.query.filter_by(slug=slug).first():
            _db.session.add(Role(slug=slug, name=name))

    if not Area.query.filter_by(name="Área de Prueba").first():
        _db.session.add(Area(name="Área de Prueba"))

    _db.session.commit()


# ─── Fixtures de usuarios de prueba ─────────────────────────────────────────

def _create_test_user(app, email: str, role_slug: str, first_name: str, area_name: str = None) -> User:
    """Helper interno para crear usuarios de test con contraseña hasheada."""
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt(app)
    with app.app_context():
        if User.query.filter_by(email=email).first():
            return User.query.filter_by(email=email).first()

        role = Role.query.filter_by(slug=role_slug).first()
        area = Area.query.filter_by(name=area_name).first() if area_name else None

        user = User(
            first_name=first_name,
            last_name="Test",
            email=email,
            password_hash=bcrypt.generate_password_hash("Test1234!").decode("utf-8"),
            role_id=role.id,
            area_id=area.id if area else None,
            is_active=True,
        )
        _db.session.add(user)
        _db.session.commit()
        return user


@pytest.fixture(scope="session")
def admin_user(app):
    """Usuario administrador de prueba."""
    return _create_test_user(app, "admin@test.ecuamatriz.local", RoleSlug.ADMIN, "Admin")


@pytest.fixture(scope="session")
def secretary_user(app):
    """Usuario secretaría de prueba."""
    return _create_test_user(app, "secretaria@test.ecuamatriz.local", RoleSlug.SECRETARY, "Secretaria")


@pytest.fixture(scope="session")
def regular_user(app):
    """Usuario colaborador de prueba."""
    return _create_test_user(
        app, "usuario@test.ecuamatriz.local", RoleSlug.USER, "Usuario", "Área de Prueba"
    )


# ─── Helpers de autenticación ────────────────────────────────────────────────

def _get_jwt_for_user(client, email: str, password: str = "Test1234!") -> str | None:
    """Obtiene access_token JWT para un usuario vía /api/auth/login."""
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        content_type="application/json",
    )
    if response.status_code == 200:
        data = response.get_json()
        return data.get("data", {}).get("access_token")
    return None


@pytest.fixture(scope="session")
def auth_headers_admin(client, admin_user):
    """Headers JWT para admin."""
    token = _get_jwt_for_user(client, admin_user.email)
    return {"Authorization": f"Bearer {token}"} if token else {}


@pytest.fixture(scope="session")
def auth_headers_secretary(client, secretary_user):
    """Headers JWT para secretaría."""
    token = _get_jwt_for_user(client, secretary_user.email)
    return {"Authorization": f"Bearer {token}"} if token else {}


@pytest.fixture(scope="session")
def auth_headers_user(client, regular_user):
    """Headers JWT para usuario colaborador."""
    token = _get_jwt_for_user(client, regular_user.email)
    return {"Authorization": f"Bearer {token}"} if token else {}
