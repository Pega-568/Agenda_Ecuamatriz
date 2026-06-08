"""Schemas Marshmallow para reuniones."""

from marshmallow import EXCLUDE, Schema, fields, validate


class MeetingCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.String(required=True, validate=validate.Length(min=1))
    objective = fields.String(required=True, validate=validate.Length(min=1))
    agenda_items = fields.List(fields.Raw(), required=True, validate=validate.Length(min=1))
    description = fields.String(allow_none=True)
    date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    modality = fields.String(required=True)
    room_id = fields.Integer(allow_none=True)
    virtual_link = fields.String(allow_none=True)
    participant_ids = fields.List(fields.Integer(), required=True, validate=validate.Length(min=1))


class MeetingRejectSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    comment = fields.String(allow_none=True)


class MeetingCancelSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    reason = fields.String(allow_none=True)


class MeetingParticipantSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Integer()
    full_name = fields.String()
    email = fields.Email()
    invitation_status = fields.String()
    attendance_status = fields.String()
    response_comment = fields.String(allow_none=True)


class MeetingResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Integer()
    title = fields.String()
    objective = fields.String()
    agenda_items = fields.List(fields.Raw())
    description = fields.String(allow_none=True)
    date = fields.String()
    start_time = fields.String()
    end_time = fields.String()
    modality = fields.String()
    status = fields.String()
    creator = fields.Dict()
    room = fields.Dict(allow_none=True)
    participants = fields.List(fields.Dict())
