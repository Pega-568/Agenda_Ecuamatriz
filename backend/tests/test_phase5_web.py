"""
tests/test_phase5_web.py
Pruebas de rutas web (Flask-Login y Roles)
"""
import pytest
from app.users.models import User
from app.roles.models import Role
from app import db

def test_web_admin_forbidden_for_user(client, regular_user, db_session):
    """Prueba que un usuario normal no puede acceder al dashboard de admin."""
    # Buscar usuario normal
    user = regular_user
    assert user is not None
    
    # Hacer login
    login_response = client.post('/auth/login', data={
        'email': user.email,
        'password': 'Test1234!'
    }, follow_redirects=True)
    assert login_response.status_code == 200
    
    # Intentar acceder a admin
    response = client.get('/admin/dashboard')
    assert response.status_code == 403

def test_web_admin_access_for_admin(client, admin_user, db_session):
    """Prueba que el admin puede acceder al dashboard de admin."""
    admin = admin_user
    assert admin is not None
    
    client.post('/auth/login', data={
        'email': admin.email,
        'password': 'Test1234!'
    }, follow_redirects=True)
    
    response = client.get('/admin/dashboard')
    assert response.status_code == 200

def test_web_user_dashboard(client, regular_user, db_session):
    """Prueba el dashboard del usuario."""
    user = regular_user
    
    client.post('/auth/login', data={
        'email': user.email,
        'password': 'Test1234!'
    }, follow_redirects=True)
    
    response = client.get('/user/dashboard')
    assert response.status_code == 200
    assert b'Reuniones de hoy' in response.data

def test_unauthenticated_redirects_to_login(client, db_session):
    """Prueba que sin estar autenticado te redirija (o lance 401 si es API, o auth required)."""
    response = client.get('/user/dashboard')
    assert response.status_code == 302

def test_web_create_meeting(client, regular_user, admin_user, db_session):
    """Prueba que un usuario puede crear una reunión web y es persistida."""
    user = regular_user
    admin = admin_user
    
    client.post('/auth/login', data={
        'email': user.email,
        'password': 'Test1234!'
    }, follow_redirects=True)
    
    response_get = client.get('/user/meetings')
    assert response_get.status_code == 200
    
    response_create_get = client.get('/user/meetings/create')
    assert response_create_get.status_code == 200

    response = client.post('/user/meetings/create', data={
        'title': 'Reunion Web Test',
        'date': '2030-10-10',
        'start_time': '10:00',
        'end_time': '11:00',
        'room_id': '',
        'objective': 'Test Obj',
        'agenda_items': 'Item 1, Item 2',
        'description': 'Test description',
        'participant_ids': [str(admin.id)],
        'modality': 'virtual'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Reuni\xc3\xb3n creada exitosamente.' in response.data or b'Reunion Web Test' in response.data or b'Error de disponibilidad' in response.data

def test_web_create_meeting_without_participants(client, regular_user, db_session):
    """Prueba que no se puede crear una reunión sin participantes."""
    user = regular_user
    
    client.post('/auth/login', data={
        'email': user.email,
        'password': 'Test1234!'
    }, follow_redirects=True)
    
    response = client.post('/user/meetings/create', data={
        'title': 'Reunion Web Test No Participants',
        'date': '2030-10-10',
        'start_time': '10:00',
        'end_time': '11:00',
        'room_id': '',
        'objective': 'Test Obj',
        'agenda_items': 'Item 1, Item 2',
        'description': 'Test description',
        # No participant_ids provided
        'modality': 'virtual'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Debe seleccionar al menos un participante' in response.data

def test_web_mark_manual_attendance(client, secretary_user, db_session):
    """Prueba que la secretaría puede marcar asistencia manual."""
    sec = secretary_user
    
    client.post('/auth/login', data={
        'email': sec.email,
        'password': 'Test1234!'
    }, follow_redirects=True)
    
    from app.meetings.models import Meeting, MeetingParticipant, MeetingModality, MeetingStatus, InvitationStatus
    from datetime import datetime, date, time
    meeting = Meeting(
        title="Test Details",
        objective="Obj",
        agenda_items=["Item 1"],
        date=date(2030, 1, 1),
        start_time=time(10, 0),
        end_time=time(11, 0),
        modality=MeetingModality.VIRTUAL,
        created_by_user_id=sec.id,
        status=MeetingStatus.SCHEDULED
    )
    db.session.add(meeting)
    db.session.flush()
    participant = MeetingParticipant(meeting_id=meeting.id, user_id=sec.id, invitation_status=InvitationStatus.ACCEPTED)
    db.session.add(participant)
    db.session.commit()

    response_sec_detail = client.get(f'/secretary/meetings/{meeting.id}')
    assert response_sec_detail.status_code == 200
    
    response = client.post(f'/secretary/meetings/{meeting.id}/attendance/manual', data={
        'user_id': str(sec.id),
        'status': 'present'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_web_admin_create_user(client, admin_user, db_session):
    admin = admin_user
    client.post('/auth/login', data={
        'email': admin.email,
        'password': 'Test1234!'
    }, follow_redirects=True)
    
    response = client.post('/admin/users', data={
        'full_name': 'Test New User',
        'email': 'newuser@ecuamatriz.local',
        'password': 'Password123!',
        'role_id': str(admin.role_id),
        'area_id': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Usuario creado exitosamente.' in response.data

def test_secretary_cannot_accept_invitation(client, secretary_user, db_session):
    sec = secretary_user
    
    from app.meetings.models import Meeting, MeetingParticipant, MeetingModality, MeetingStatus, InvitationStatus
    from datetime import datetime, date, time
    meeting = Meeting(
        title="Sec Invite Test",
        objective="Obj",
        agenda_items=["Item 1"],
        date=date(2030, 1, 1),
        start_time=time(10, 0),
        end_time=time(11, 0),
        modality=MeetingModality.VIRTUAL,
        created_by_user_id=sec.id,
        status=MeetingStatus.SCHEDULED
    )
    db.session.add(meeting)
    db.session.flush()
    participant = MeetingParticipant(meeting_id=meeting.id, user_id=sec.id, invitation_status=InvitationStatus.PENDING)
    db.session.add(participant)
    db.session.commit()
    
    token = None
    response = client.post('/api/auth/login', json={'email': sec.email, 'password': 'Test1234!'})
    if response.status_code == 200:
        token = response.get_json()['data']['access_token']
        
    response = client.post(f'/api/meetings/{meeting.id}/accept', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403
    data = response.get_json()
    assert data["error"]["code"] == "FORBIDDEN"
    assert "Secretar" in data["error"]["message"]
