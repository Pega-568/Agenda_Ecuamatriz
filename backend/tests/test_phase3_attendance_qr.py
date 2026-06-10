from datetime import date, datetime, timedelta
from urllib.parse import urlparse

from app import db
from app.audit.models import AuditLog
from app.attendance.models import AttendanceToken
from app.meetings.models import AttendanceMethod, AttendanceStatus, InvitationStatus, Meeting, MeetingParticipant, MeetingStatus
from app.roles.models import Role, RoleSlug
from app.settings.models import SystemSetting
from app.settings.service import SettingsService
from app.users.service import UserService


def _make_user(email, role_slug=RoleSlug.USER, active=True):
    role = Role.query.filter_by(slug=role_slug).first()
    return UserService.create_user(
        {
            "full_name": email.split("@")[0].replace(".", " ").title(),
            "email": email,
            "password": "Test1234!",
            "role_id": role.id,
            "is_active": active,
        }
    )


def _token(client, email, password="Test1234!"):
    from app.users.models import User
    from flask_jwt_extended import create_access_token
    user = User.query.filter_by(email=email).first()
    return create_access_token(identity=str(user.id))

def _headers(client, user):
    return {"Authorization": f"Bearer {_token(client, user.email)}"}


def _meeting(creator, participant, invitation_status=InvitationStatus.ACCEPTED, status=MeetingStatus.SCHEDULED, starts_delta=5, ends_delta=35):
    now = datetime.now()
    meeting = Meeting(
        title="Reunión QR",
        objective="Validar asistencia",
        agenda_items=["QR"],
        date=date.today(),
        start_time=(now + timedelta(minutes=starts_delta)).time().replace(second=0, microsecond=0),
        end_time=(now + timedelta(minutes=ends_delta)).time().replace(second=0, microsecond=0),
        modality="virtual",
        created_by_user_id=creator.id,
        status=status,
    )
    db.session.add(meeting)
    db.session.flush()
    db.session.add(MeetingParticipant(meeting_id=meeting.id, user_id=participant.id, invitation_status=invitation_status))
    db.session.commit()
    return meeting


def _plain_token(payload):
    return urlparse(payload["attendance_url"]).path.rsplit("/", 1)[-1]


def test_creator_secretary_permissions_and_single_active_token(client, db_session, regular_user, secretary_user, admin_user):
    invitee = _make_user("qr.invitee@test.local")
    outsider = _make_user("qr.outsider@test.local")
    meeting = _meeting(regular_user, invitee)

    first = client.post(f"/api/meetings/{meeting.id}/attendance-token", headers=_headers(client, regular_user))
    assert first.status_code == 200
    first_data = first.get_json()["data"]
    assert first_data["token_available"] is True
    assert first_data["attendance_url"]
    assert AttendanceToken.query.count() == 1
    assert AttendanceToken.query.first().token_hash
    assert not hasattr(AttendanceToken.query.first(), "token")
    assert AuditLog.query.filter_by(action="attendance_token_created").count() == 1

    second = client.post(f"/api/meetings/{meeting.id}/attendance-token", headers=_headers(client, regular_user))
    assert second.status_code == 200
    assert second.get_json()["data"]["token_available"] is True
    assert AttendanceToken.query.filter_by(meeting_id=meeting.id, is_active=True).count() == 1

    secretary_response = client.post(f"/api/meetings/{meeting.id}/attendance-token", headers=_headers(client, secretary_user))
    assert secretary_response.status_code == 200
    assert client.post(f"/api/meetings/{meeting.id}/attendance-token", headers=_headers(client, admin_user)).status_code == 403
    assert client.post(f"/api/meetings/{meeting.id}/attendance-token", headers=_headers(client, outsider)).status_code == 403


def test_cancelled_meeting_does_not_generate_token(client, db_session, regular_user):
    invitee = _make_user("cancelled.qr@test.local")
    meeting = _meeting(regular_user, invitee, status=MeetingStatus.CANCELLED)
    response = client.post(f"/api/meetings/{meeting.id}/attendance-token", headers=_headers(client, regular_user))
    assert response.status_code == 409


def test_qr_invalid_disabled_unauthenticated_and_wrong_user(client, db_session, regular_user):
    invitee = _make_user("scan.invitee@test.local")
    outsider = _make_user("scan.outsider@test.local")
    meeting = _meeting(regular_user, invitee)
    token_payload = client.post(f"/api/meetings/{meeting.id}/attendance-token", headers=_headers(client, regular_user)).get_json()["data"]
    token = _plain_token(token_payload)

    assert client.post("/api/attendance/qr/not-a-token", headers=_headers(client, invitee)).status_code == 409
    assert client.post(f"/api/attendance/qr/{token}").status_code == 401
    assert client.post(f"/api/attendance/qr/{token}", headers=_headers(client, outsider)).status_code == 403

    SettingsService.update_settings({"qr_attendance_enabled": False})
    assert client.post(f"/api/attendance/qr/{token}", headers=_headers(client, invitee)).status_code == 409


def test_qr_requires_accepted_invitation_and_blocks_rejected_or_pending(client, db_session, regular_user):
    pending = _make_user("pending.qr@test.local")
    rejected = _make_user("rejected.qr@test.local")
    pending_meeting = _meeting(regular_user, pending, InvitationStatus.PENDING)
    rejected_meeting = _meeting(regular_user, rejected, InvitationStatus.REJECTED)
    pending_token = _plain_token(client.post(f"/api/meetings/{pending_meeting.id}/attendance-token", headers=_headers(client, regular_user)).get_json()["data"])
    rejected_token = _plain_token(client.post(f"/api/meetings/{rejected_meeting.id}/attendance-token", headers=_headers(client, regular_user)).get_json()["data"])

    assert client.post(f"/api/attendance/qr/{pending_token}", headers=_headers(client, pending)).status_code == 409
    assert client.post(f"/api/attendance/qr/{rejected_token}", headers=_headers(client, rejected)).status_code == 409


def test_qr_window_before_after_and_successful_marking(client, db_session, regular_user):
    before_user = _make_user("before.window@test.local")
    before_meeting = _meeting(regular_user, before_user, starts_delta=40, ends_delta=70)
    before_token = _plain_token(client.post(f"/api/meetings/{before_meeting.id}/attendance-token", headers=_headers(client, regular_user)).get_json()["data"])
    assert client.post(f"/api/attendance/qr/{before_token}", headers=_headers(client, before_user)).status_code == 409

    after_user = _make_user("after.window@test.local")
    after_meeting = _meeting(regular_user, after_user, starts_delta=-70, ends_delta=-40)
    after_token = _plain_token(client.post(f"/api/meetings/{after_meeting.id}/attendance-token", headers=_headers(client, regular_user)).get_json()["data"])
    assert client.post(f"/api/attendance/qr/{after_token}", headers=_headers(client, after_user)).status_code == 409

    invitee = _make_user("inside.window@test.local")
    meeting = _meeting(regular_user, invitee)
    token = _plain_token(client.post(f"/api/meetings/{meeting.id}/attendance-token", headers=_headers(client, regular_user)).get_json()["data"])
    response = client.post(f"/api/attendance/qr/{token}", headers=_headers(client, invitee))
    assert response.status_code == 200, response.get_data(as_text=True)
    data = response.get_json()["data"]
    assert data["attendance_status"] == AttendanceStatus.PRESENT
    assert data["attendance_method"] == AttendanceMethod.QR

    participant = MeetingParticipant.query.filter_by(meeting_id=meeting.id, user_id=invitee.id).first()
    assert participant.attendance_status == AttendanceStatus.PRESENT
    assert participant.attendance_method == AttendanceMethod.QR
    assert participant.attendance_marked_at is not None
    assert AuditLog.query.filter_by(action="attendance_marked_qr").count() == 1
    assert client.post(f"/api/attendance/qr/{token}", headers=_headers(client, invitee)).status_code == 409


def test_cancelled_meeting_does_not_allow_qr_marking(client, db_session, regular_user):
    invitee = _make_user("cancelled.mark@test.local")
    meeting = _meeting(regular_user, invitee)
    token = _plain_token(client.post(f"/api/meetings/{meeting.id}/attendance-token", headers=_headers(client, regular_user)).get_json()["data"])
    meeting.status = MeetingStatus.CANCELLED
    db.session.commit()
    assert client.post(f"/api/attendance/qr/{token}", headers=_headers(client, invitee)).status_code == 409


def test_attendance_report_permissions_and_summary(client, db_session, regular_user, secretary_user, admin_user):
    present = _make_user("present.report@test.local")
    absent = _make_user("absent.report@test.local")
    outsider = _make_user("outsider.report@test.local")
    meeting = _meeting(regular_user, present)
    db.session.add(MeetingParticipant(meeting_id=meeting.id, user_id=absent.id, invitation_status=InvitationStatus.ACCEPTED, attendance_status=AttendanceStatus.ABSENT))
    db.session.commit()

    assert client.get(f"/api/meetings/{meeting.id}/attendance", headers=_headers(client, admin_user)).status_code == 403
    assert client.get(f"/api/meetings/{meeting.id}/attendance", headers=_headers(client, outsider)).status_code == 403
    creator_response = client.get(f"/api/meetings/{meeting.id}/attendance", headers=_headers(client, regular_user))
    secretary_response = client.get(f"/api/meetings/{meeting.id}/attendance", headers=_headers(client, secretary_user))
    assert creator_response.status_code == 200
    assert secretary_response.status_code == 200
    summary = creator_response.get_json()["data"]["summary"]
    assert summary["total_invited"] == 2
    assert summary[AttendanceStatus.NOT_MARKED] == 1
    assert summary[AttendanceStatus.ABSENT] == 1


def test_manual_attendance_permissions_settings_methods_and_audit(client, db_session, regular_user, secretary_user, admin_user):
    invitee = _make_user("manual.invitee@test.local")
    rejected = _make_user("manual.rejected@test.local")
    outsider = _make_user("manual.outsider@test.local")
    meeting = _meeting(regular_user, invitee)
    db.session.add(MeetingParticipant(meeting_id=meeting.id, user_id=rejected.id, invitation_status=InvitationStatus.REJECTED))
    db.session.commit()

    payload = {"user_id": invitee.id, "attendance_status": AttendanceStatus.PRESENT, "comment": "Manual"}
    assert client.post(f"/api/meetings/{meeting.id}/attendance/manual", json=payload, headers=_headers(client, admin_user)).status_code == 403
    assert client.post(f"/api/meetings/{meeting.id}/attendance/manual", json=payload, headers=_headers(client, outsider)).status_code == 403
    assert client.post(f"/api/meetings/{meeting.id}/attendance/manual", json=payload, headers=_headers(client, regular_user)).status_code == 403

    response = client.post(f"/api/meetings/{meeting.id}/attendance/manual", json=payload, headers=_headers(client, secretary_user))
    assert response.status_code == 200, response.get_data(as_text=True)
    participant = MeetingParticipant.query.filter_by(meeting_id=meeting.id, user_id=invitee.id).first()
    assert participant.attendance_method == AttendanceMethod.MANUAL_SECRETARY
    assert participant.attendance_marked_by_user_id == secretary_user.id
    assert AuditLog.query.filter_by(action="attendance_marked_manual").count() == 1

    SettingsService.update_settings({"allow_manual_attendance_by_secretary": False})
    assert client.post(f"/api/meetings/{meeting.id}/attendance/manual", json=payload, headers=_headers(client, secretary_user)).status_code == 403

    SettingsService.update_settings({"allow_manual_attendance_by_creator": True, "allow_manual_attendance_by_secretary": True})
    creator_payload = {"user_id": invitee.id, "attendance_status": AttendanceStatus.JUSTIFIED, "comment": "Justificado"}
    response = client.post(f"/api/meetings/{meeting.id}/attendance/manual", json=creator_payload, headers=_headers(client, regular_user))
    assert response.status_code == 200
    assert MeetingParticipant.query.filter_by(meeting_id=meeting.id, user_id=invitee.id).first().attendance_method == AttendanceMethod.MANUAL_CREATOR

    rejected_payload = {"user_id": rejected.id, "attendance_status": AttendanceStatus.PRESENT}
    assert client.post(f"/api/meetings/{meeting.id}/attendance/manual", json=rejected_payload, headers=_headers(client, secretary_user)).status_code == 409
    rejected_payload["comment"] = "Autorizado por Secretaría"
    assert client.post(f"/api/meetings/{meeting.id}/attendance/manual", json=rejected_payload, headers=_headers(client, secretary_user)).status_code == 200


def test_seed_adds_qr_settings_idempotently(db_session):
    SettingsService.seed_defaults()
    SettingsService.seed_defaults()
    keys = {
        "qr_attendance_enabled",
        "qr_valid_before_minutes",
        "qr_valid_after_minutes",
        "allow_manual_attendance_by_secretary",
        "allow_manual_attendance_by_creator",
        "require_login_for_qr_attendance",
    }
    assert keys.issubset({setting.key for setting in SystemSetting.query.all()})
    assert SystemSetting.query.filter(SystemSetting.key.in_(keys)).count() == len(keys)
