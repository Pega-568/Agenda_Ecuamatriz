"""Schemas Marshmallow para disponibilidad."""

from marshmallow import EXCLUDE, Schema, fields


class AvailabilityCheckSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    room_id = fields.Integer(required=False, allow_none=True)
    participant_ids = fields.List(fields.Integer(), load_default=list)


class AvailabilityResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    can_create = fields.Boolean()
    hard_blocks = fields.List(fields.Dict())
    warnings = fields.List(fields.Dict())
    room = fields.Dict(allow_none=True)
    participants = fields.List(fields.Dict())
    suggested_slots = fields.List(fields.Dict())
