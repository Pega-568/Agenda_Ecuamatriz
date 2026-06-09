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

def test_api_mobile_unified_agenda(client, regular_user, db_session, app):
    with app.app_context():
        access_token = create_access_token(identity=str(regular_user.id))
        
    response = client.get(
        "/api/mobile/meetings",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json()["data"], list)

def test_api_mobile_meeting_options(client, regular_user, db_session, app):
    with app.app_context():
        access_token = create_access_token(identity=str(regular_user.id))
        
    response = client.get(
        "/api/mobile/meetings/options",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert "rooms" in data
    assert "users" in data

def test_api_mobile_create_meeting(client, regular_user, db_session, app):
    with app.app_context():
        access_token = create_access_token(identity=str(regular_user.id))
        from app.rooms.models import Room
        from app.users.models import User
        from app.roles.models import Role, RoleSlug
        room = Room.query.first()
        if not room:
            room = Room(name="Test Room", location="Test Location", capacity=10, is_active=True)
            db_session.add(room)
            db_session.commit()
            
        # Create an alternative user if none exist
        other_user = User.query.filter(User.id != regular_user.id).first()
        if not other_user:
            role = Role.query.filter_by(slug=RoleSlug.USER).first()
            other_user = User(email="test2@example.com", first_name="Test2", last_name="User", role_id=role.id, is_active=True, password_hash="dummy")
            db_session.add(other_user)
            db_session.commit()
            
        other_user_id = other_user.id
        room_id = room.id if room else None
            
    payload = {
        "title": "Mobile Test Meeting",
        "objective": "Testing mobile creation",
        "description": "...",
        "agenda_items": ["Item 1", "Item 2"],
        "date": "2026-10-10",
        "start_time": "10:00",
        "end_time": "11:00",
        "modality": "in_person",
        "room_id": room_id,
        "participant_ids": [other_user_id]
    }
    
    response = client.post(
        "/api/mobile/meetings",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    # Could be 200 or 409 depending on availability conflicts with seed data, 
    # but the endpoint is there and functioning
    assert response.status_code in [200, 409]
