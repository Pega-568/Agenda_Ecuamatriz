"""
tests/test_health.py — Tests de sanidad del servidor
Agenda Ecuamatriz

Verifica que:
    - La app Flask arranca correctamente.
    - El endpoint /health responde.
    - Todos los blueprints están registrados.
    - Las rutas de error devuelven formato JSON correcto.

Estos tests NO requieren datos de negocio, solo que la app arranque.
Usan PostgreSQL (Docker) via conftest.py.
"""


def test_app_starts(client):
    """La aplicación Flask debe instanciarse sin errores."""
    assert client is not None


def test_health_endpoint_ok(client):
    """
    GET /health debe retornar 200 con estado ok cuando la BD está disponible.
    La BD de test es PostgreSQL Docker.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert "app" in data


def test_unknown_route_returns_404_json(client):
    """Rutas no registradas deben retornar 404 con formato JSON estándar."""
    response = client.get("/api/ruta-que-no-existe-jamas")
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert data["success"] is False
    assert "error" in data


def test_auth_web_login_route_exists(client):
    """
    GET /auth/login debe existir (auth web con Flask-Login).
    En Fase 0 retorna 501 (stub). Verificar que no da 404.
    """
    response = client.get("/auth/login")
    assert response.status_code in (200, 302, 501), (
        f"GET /auth/login retornó {response.status_code} — ¿Blueprint auth_web_bp no registrado?"
    )


def test_auth_api_login_route_exists(client):
    """
    POST /api/auth/login debe existir (auth API JWT para Android).
    En Fase 0 retorna 501 (stub). Verificar que no da 404.
    """
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password"},
        content_type="application/json",
    )
    assert response.status_code in (200, 401, 422, 501), (
        f"POST /api/auth/login retornó {response.status_code} — ¿Blueprint auth_api_bp no registrado?"
    )


def test_all_api_module_stubs_registered(client):
    """
    Verifica que todos los blueprints /api/ están registrados.
    Todos deben retornar 501 (stub) o error de auth (401/403), nunca 404.
    """
    stub_endpoints = [
        ("GET",  "/api/users/"),
        ("GET",  "/api/areas/"),
        ("GET",  "/api/rooms/"),
        ("GET",  "/api/settings/"),
        ("GET",  "/api/calendar/days"),
        ("GET",  "/api/meetings/"),
        ("GET",  "/api/notifications/"),
        ("GET",  "/api/audit/"),
        ("GET",  "/api/recordings/1"),
        ("GET",  "/api/transcriptions/1"),
    ]

    for method, url in stub_endpoints:
        response = client.open(url, method=method)
        assert response.status_code != 404, (
            f"{method} {url} retornó 404 — Blueprint NO registrado. "
            "Revisar _register_blueprints() en app/__init__.py"
        )
        assert response.status_code in (200, 201, 400, 401, 403, 422, 501), (
            f"{method} {url} retornó código inesperado: {response.status_code}"
        )
