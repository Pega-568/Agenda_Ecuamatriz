"""Schemas Marshmallow para areas."""

from marshmallow import EXCLUDE, Schema, fields


class AreaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True)
    description = fields.String(allow_none=True)
    is_active = fields.Boolean(load_default=True)
