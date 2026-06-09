"""Schemas de asistencia."""

from marshmallow import Schema, fields, validate

from app.meetings.models import AttendanceStatus


class ManualAttendanceSchema(Schema):
    user_id = fields.Integer(required=True)
    attendance_status = fields.String(required=True, validate=validate.OneOf(AttendanceStatus.ALL))
    comment = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=500))
