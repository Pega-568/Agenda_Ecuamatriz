from flask_jwt_extended import create_access_token, create_refresh_token
import pytest
from app.users.models import MobileDeviceToken

def test_api_login_returns_tokens(client, regular_user, db_session):
    response = client.post("/api/auth/login", json={"email": regular_user.email, "password": "Test1234!"})
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == regular_user.email

def test_api_refresh_token(client, regular_user, db_session, app):
    with app.app_context():
        refresh_token = create_refresh_token(identity=str(regular_user.id)) # Simular refresh
    
    response = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 200
    assert "access_token" in response.get_json()["data"]

def test_api_register_device(client, regular_user, db_session, app):
    with app.app_context():
        access_token = create_access_token(identity=str(regular_user.id))
    
    response = client.post(
        "/api/auth/devices/register",
        json={"fcm_token": "test-fcm-token-123"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    
    token_obj = MobileDeviceToken.query.filter_by(fcm_token="test-fcm-token-123").first()
    assert token_obj is not None
    assert token_obj.user_id == regular_user.id

def test_api_mobile_meetings_today(client, regular_user, db_session, app):
    with app.app_context():
        access_token = create_access_token(identity=str(regular_user.id))
        
    response = client.get(
        "/api/mobile/meetings/today",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json()["data"], list)

def test_api_mobile_meetings_invitations(client, regular_user, db_session, app):
    with app.app_context():
        access_token = create_access_token(identity=str(regular_user.id))
        
    response = client.get(
        "/api/mobile/meetings/invitations",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json()["data"], list)

def test_api_logout(client, regular_user, db_session, app):
    with app.app_context():
        access_token = create_access_token(identity=str(regular_user.id))
        
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
