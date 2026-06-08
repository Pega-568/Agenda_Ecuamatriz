"""Schemas Marshmallow para salas."""

from marshmallow import EXCLUDE, Schema, fields


class RoomSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True)
    location = fields.String(allow_none=True)
    capacity = fields.Integer(required=True)
    description = fields.String(allow_none=True)
    has_projector = fields.Boolean(load_default=False)
    has_video_conference = fields.Boolean(load_default=False)
    is_active = fields.Boolean(load_default=True)
