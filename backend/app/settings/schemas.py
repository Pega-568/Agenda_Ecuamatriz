"""Schemas Marshmallow para settings."""

from marshmallow import EXCLUDE, Schema, fields


class SettingsUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    max_meeting_participants = fields.Raw()
    max_meeting_duration_minutes = fields.Raw()
    min_meeting_notice_minutes = fields.Raw()
    allow_meetings_outside_work_hours = fields.Raw()
    allow_meetings_on_non_working_days = fields.Raw()
    qr_valid_before_minutes = fields.Raw()
    qr_valid_after_minutes = fields.Raw()
    web_notifications_enabled = fields.Raw()
    mobile_notifications_enabled = fields.Raw()
