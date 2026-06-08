"""Schemas Marshmallow para calendario laboral."""

from marshmallow import EXCLUDE, Schema, fields


class WorkScheduleSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    is_working_day = fields.Boolean()
    start_time = fields.String(allow_none=True)
    end_time = fields.String(allow_none=True)
