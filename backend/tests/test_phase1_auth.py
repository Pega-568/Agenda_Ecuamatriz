from flask_login import current_user

from app.auth.service import AuthService
from app.users.service import UserService


def test_web_login_correct(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"email": admin_user.email, "password": "Test1234!"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/auth/dashboard" in response.headers["Location"]


def test_web_login_incorrect(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"email": admin_user.email, "password": "bad-password"},
    )
    assert response.status_code in [302, 401]


def test_inactive_user_cannot_authenticate(db_session, admin_user):
    UserService.set_active(admin_user.id, False)
    assert AuthService.authenticate(admin_user.email, "Test1234!") is None


def test_logout(client, admin_user):
    client.post("/auth/login", data={"email": admin_user.email, "password": "Test1234!"})
    response = client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 302


def test_api_login_and_me(client, admin_user):
    response = client.post("/api/auth/login", json={"email": admin_user.email, "password": "Test1234!"})
    assert response.status_code == 200
    token = response.get_json()["data"]["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.get_json()["data"]["email"] == admin_user.email
