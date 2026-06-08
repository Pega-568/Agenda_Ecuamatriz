from datetime import date, timedelta

import pytest

from app import db
from app.areas.models import Area
from app.audit.models import AuditLog
from app.calendar.models import WorkCalendarDay
from app.calendar.service import WorkScheduleService
from app.meetings.models import InvitationStatus, Meeting, MeetingParticipant, MeetingStatus
from app.notifications.models import Notification
from app.roles.models import Role, RoleSlug
from app.rooms.service import RoomService
from app.settings.service import SettingsService
from app.users.service import UserService


def _meeting_date():
    target = date.today() + timedelta(days=14)
    while target.isoweekday() > 5:
        target += timedelta(days=1)
    return target


def _seed_base():
    from app.roles.service import RoleService

    RoleService.seed_defaults()
    WorkScheduleService.seed_defaults()
    SettingsService.seed_defaults()
    area = Area.query.filter_by(name="Área de Prueba").first()
    if not area:
        area = Area(name="Área de Prueba")
        db.session.add(area)
        db.session.commit()
    room = RoomService.create_room({"name": f"Sala {_meeting_date().isoformat()}", "capacity": 10})
    return area, room


def _make_user(email, role_slug=RoleSlug.USER, area_id=None, active=True):
    role = Role.query.filter_by(slug=role_slug).first()
    name = email.split("@")[0].replace(".", " ").title()
    if " " not in name:
        name = f"{name} Test"
    return UserService.create_user(
        {
            "full_name": name,
            "email": email,
            "password": "Test1234!",
            "role_id": role.id,
            "area_id": area_id,
            "is_active": active,
        }
    )


def _token(client, email, password="Test1234!"):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.get_data(as_text=True)
    return response.get_json()["data"]["access_token"]


def _headers(client, user):
    return {"Authorization": f"Bearer {_token(client, user.email)}"}


def _payload(room, participants, **overrides):
    data = {
        "title": "Revisión de avances",
        "objective": "Revisar avances semanales",
        "agenda_items": ["Revisión de pendientes", "Problemas", "Próximos compromisos"],
        "description": "Opcional",
        "date": _meeting_date().isoformat(),
        "start_time": "10:00",
        "end_time": "11:00",
        "modality": "presencial",
        "room_id": room.id,
        "participant_ids": [user.id for user in participants],
    }
    data.update(overrides)
    return data


def _create_meeting(client, creator, room, participants, **overrides):
    response = client.post("/api/meetings", json=_payload(room, participants, **overrides), headers=_headers(client, creator))
    assert response.status_code == 201, response.get_data(as_text=True)
    return response.get_json()["data"]["meeting"]


def test_user_search_for_meetings_excludes_inactive_and_admin(client, db_session):
    area, _room = _seed_base()
    active = _make_user("juan.produccion@test.local", area_id=area.id)
    _make_user("admin.search@test.local", RoleSlug.ADMIN, area.id)
    _make_user("inactive.search@test.local", RoleSlug.USER, area.id, active=False)

    response = client.get(f"/api/users/search?q=juan&area_id={area.id}")
    assert response.status_code == 200
    items = response.get_json()["data"]["items"]
    assert [item["id"] for item in items] == [active.id]


def test_admin_cannot_create_meeting(client, db_session, admin_user):
    area, room = _seed_base()
    participant = _make_user("participant.admin.block@test.local", area_id=area.id)
    response = client.post("/api/meetings", json=_payload(room, [participant]), headers=_headers(client, admin_user))
    assert response.status_code == 403


def test_user_and_secretary_can_create_valid_meetings(client, db_session, regular_user, secretary_user):
    area, room = _seed_base()
    p1 = _make_user("p1.valid@test.local", area_id=area.id)
    p2 = _make_user("p2.valid@test.local", area_id=area.id)

    assert _create_meeting(client, regular_user, room, [p1])["title"] == "Revisión de avances"
    room2 = RoomService.create_room({"name": "Sala Secretaria", "capacity": 10})
    assert _create_meeting(client, secretary_user, room2, [p2])["creator"]["email"] == secretary_user.email


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", ""),
        ("objective", ""),
        ("agenda_items", []),
    ],
)
def test_required_meeting_fields_fail(client, db_session, regular_user, field, value):
    area, room = _seed_base()
    participant = _make_user(f"{field}.required@test.local", area_id=area.id)
    payload = _payload(room, [participant])
    payload[field] = value
    response = client.post("/api/meetings", json=payload, headers=_headers(client, regular_user))
    assert response.status_code == 422


def test_invalid_time_duration_and_participant_limit_fail(client, db_session, regular_user):
    area, room = _seed_base()
    p1 = _make_user("p1.limit@test.local", area_id=area.id)
    p2 = _make_user("p2.limit@test.local", area_id=area.id)

    response = client.post("/api/meetings", json=_payload(room, [p1], start_time="11:00", end_time="10:00"), headers=_headers(client, regular_user))
    assert response.status_code in (409, 422)

    response = client.post("/api/meetings", json=_payload(room, [p1], start_time="08:00", end_time="13:00"), headers=_headers(client, regular_user))
    assert response.status_code == 409

    SettingsService.update_settings({"max_meeting_participants": 1})
    response = client.post("/api/meetings", json=_payload(room, [p1, p2]), headers=_headers(client, regular_user))
    assert response.status_code == 409


def test_inactive_admin_participant_and_inactive_room_block(client, db_session, regular_user):
    area, room = _seed_base()
    inactive = _make_user("inactive.invite@test.local", area_id=area.id, active=False)
    admin = _make_user("admin.invite@test.local", RoleSlug.ADMIN, area.id)
    inactive_room = RoomService.create_room({"name": "Sala Inactiva", "capacity": 10})
    RoomService.set_active(inactive_room.id, False)

    for participant, target_room in [(inactive, room), (admin, room), (_make_user("ok.room@test.local", area_id=area.id), inactive_room)]:
        response = client.post("/api/meetings", json=_payload(target_room, [participant]), headers=_headers(client, regular_user))
        assert response.status_code == 409


def test_room_non_working_day_and_outside_hours_block(client, db_session, regular_user):
    area, room = _seed_base()
    p1 = _make_user("p1.blocks@test.local", area_id=area.id)
    _create_meeting(client, regular_user, room, [p1])
    p2 = _make_user("p2.blocks@test.local", area_id=area.id)
    response = client.post("/api/meetings", json=_payload(room, [p2]), headers=_headers(client, regular_user))
    assert response.status_code == 409

    blocked_date = _meeting_date() + timedelta(days=1)
    db.session.add(WorkCalendarDay(date=blocked_date, is_working_day=False, blocks_meetings=True, label="Feriado"))
    db.session.commit()
    room2 = RoomService.create_room({"name": "Sala Feriado", "capacity": 10})
    response = client.post("/api/meetings", json=_payload(room2, [p2], date=blocked_date.isoformat()), headers=_headers(client, regular_user))
    assert response.status_code == 409

    room3 = RoomService.create_room({"name": "Sala Fuera Horario", "capacity": 10})
    response = client.post("/api/meetings", json=_payload(room3, [p2], start_time="18:00", end_time="19:00"), headers=_headers(client, regular_user))
    assert response.status_code == 409


def test_availability_participant_states_and_blocking_rules(client, db_session, regular_user):
    area, room = _seed_base()
    pending_user = _make_user("pending@test.local", area_id=area.id)
    rejected_user = _make_user("rejected@test.local", area_id=area.id)
    accepted_user = _make_user("accepted@test.local", area_id=area.id)
    busy_creator = _make_user("creator.busy@test.local", area_id=area.id)

    meeting_pending = _create_meeting(client, regular_user, room, [pending_user, rejected_user, accepted_user])
    client.post(f"/api/meetings/{meeting_pending['id']}/reject", json={"comment": "Cruce"}, headers=_headers(client, rejected_user))
    client.post(f"/api/meetings/{meeting_pending['id']}/accept", headers=_headers(client, accepted_user))

    room2 = RoomService.create_room({"name": "Sala Estados", "capacity": 10})
    check = client.post(
        "/api/meetings/check-availability",
        json=_payload(room2, [pending_user, rejected_user, accepted_user]),
        headers=_headers(client, busy_creator),
    )
    assert check.status_code == 200
    statuses = {p["id"]: p["status"] for p in check.get_json()["data"]["participants"]}
    assert statuses[pending_user.id] == "pending"
    assert statuses[rejected_user.id] == "rejected"
    assert statuses[accepted_user.id] == "busy"

    _create_meeting(client, busy_creator, RoomService.create_room({"name": "Sala Creador", "capacity": 10}), [_make_user("creator.invited@test.local", area_id=area.id)])
    response = client.post("/api/meetings", json=_payload(RoomService.create_room({"name": "Sala Creador 2", "capacity": 10}), [pending_user]), headers=_headers(client, busy_creator))
    assert response.status_code == 409


def test_accept_reject_cancel_notifications_and_audit(client, db_session, regular_user):
    area, room = _seed_base()
    invitee = _make_user("invitee.actions@test.local", area_id=area.id)
    meeting = _create_meeting(client, regular_user, room, [invitee])
    assert Notification.query.filter_by(user_id=invitee.id, type="meeting_invitation").count() == 1
    assert AuditLog.query.filter_by(action="meeting_created").count() == 1

    response = client.post(f"/api/meetings/{meeting['id']}/accept", headers=_headers(client, invitee))
    assert response.status_code == 200
    assert Notification.query.filter_by(user_id=regular_user.id, type="meeting_accepted").count() == 1

    second = _make_user("invitee.reject@test.local", area_id=area.id)
    room2 = RoomService.create_room({"name": "Sala Rechazo", "capacity": 10})
    meeting2 = _create_meeting(client, regular_user, room2, [second], start_time="11:00", end_time="12:00")
    response = client.post(f"/api/meetings/{meeting2['id']}/reject", json={"comment": "No puedo"}, headers=_headers(client, second))
    assert response.status_code == 200
    assert Notification.query.filter_by(user_id=regular_user.id, type="meeting_rejected").count() == 1
    assert MeetingParticipant.query.filter_by(meeting_id=meeting2["id"], user_id=second.id).first().invitation_status == InvitationStatus.REJECTED

    response = client.post(f"/api/meetings/{meeting['id']}/cancel", json={"reason": "Cambio"}, headers=_headers(client, regular_user))
    assert response.status_code == 200
    assert db.session.get(Meeting, meeting["id"]).status == MeetingStatus.CANCELLED
    assert Notification.query.filter_by(user_id=invitee.id, type="meeting_cancelled").count() == 1
    assert AuditLog.query.filter_by(action="meeting_cancelled").count() == 1


def test_accept_blocks_if_confirmed_conflict(client, db_session, regular_user):
    area, room = _seed_base()
    invitee = _make_user("conflict.accept@test.local", area_id=area.id)
    other_creator = _make_user("other.creator@test.local", area_id=area.id)
    _create_meeting(client, regular_user, room, [invitee])
    client.post(f"/api/meetings/{Meeting.query.first().id}/accept", headers=_headers(client, invitee))

    meeting2 = _create_meeting(client, other_creator, RoomService.create_room({"name": "Sala Conflicto Aceptar", "capacity": 10}), [invitee])
    response = client.post(f"/api/meetings/{meeting2['id']}/accept", headers=_headers(client, invitee))
    assert response.status_code == 409


def test_meeting_list_detail_permissions_secretary_and_admin(client, db_session, regular_user, secretary_user, admin_user):
    area, room = _seed_base()
    invitee = _make_user("list.invitee@test.local", area_id=area.id)
    outsider = _make_user("outsider@test.local", area_id=area.id)
    meeting = _create_meeting(client, regular_user, room, [invitee])

    assert client.get("/api/meetings", headers=_headers(client, regular_user)).status_code == 200
    assert client.get("/api/meetings", headers=_headers(client, invitee)).status_code == 200
    assert client.get("/api/meetings", headers=_headers(client, secretary_user)).status_code == 200
    assert client.get("/api/meetings", headers=_headers(client, admin_user)).status_code == 403

    assert client.get(f"/api/meetings/{meeting['id']}", headers=_headers(client, regular_user)).status_code == 200
    assert client.get(f"/api/meetings/{meeting['id']}", headers=_headers(client, invitee)).status_code == 200
    assert client.get(f"/api/meetings/{meeting['id']}", headers=_headers(client, secretary_user)).status_code == 200
    assert client.get(f"/api/meetings/{meeting['id']}", headers=_headers(client, outsider)).status_code == 403
    assert client.get(f"/api/meetings/{meeting['id']}", headers=_headers(client, admin_user)).status_code == 403
