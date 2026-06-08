import pytest

from app.calendar.service import WorkScheduleService
from app.settings.service import SettingsService


def test_read_and_update_settings(db_session):
    SettingsService.seed_defaults()
    settings = SettingsService.list_settings()
    assert "max_meeting_participants" in {setting.key for setting in settings}

    updated = SettingsService.update_settings({"max_meeting_participants": 12})
    assert updated[0].get_typed_value() == 12


def test_reject_invalid_settings(db_session):
    SettingsService.seed_defaults()
    with pytest.raises(ValueError):
        SettingsService.update_settings({"max_meeting_participants": -1})
    with pytest.raises(ValueError):
        SettingsService.update_settings({"web_notifications_enabled": "maybe"})


def test_work_schedule_defaults(db_session):
    schedules = WorkScheduleService.seed_defaults()
    by_weekday = {schedule.weekday: schedule for schedule in schedules}
    assert all(by_weekday[weekday].is_working_day for weekday in range(1, 6))
    assert by_weekday[6].is_working_day is False
    assert by_weekday[7].is_working_day is False


def test_reject_invalid_work_schedule_hours(db_session):
    WorkScheduleService.seed_defaults()
    with pytest.raises(ValueError):
        WorkScheduleService.update_schedule(1, {"is_working_day": True, "start_time": "17:00", "end_time": "08:00"})
