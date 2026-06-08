"""Schemas Marshmallow para usuarios."""

from marshmallow import EXCLUDE, Schema, fields


class UserCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    role_id = fields.Integer(required=True)
    area_id = fields.Integer(allow_none=True)
    phone = fields.String(allow_none=True)
    position = fields.String(allow_none=True)
    is_active = fields.Boolean(load_default=True)


class UserUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    password = fields.String(load_only=True)
    role_id = fields.Integer()
    area_id = fields.Integer(allow_none=True)
    phone = fields.String(allow_none=True)
    position = fields.String(allow_none=True)
