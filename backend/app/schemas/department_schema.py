"""
app/schemas/department_schema.py
─────────────────────────────────
Marshmallow validation schemas for Department endpoints.
"""

from marshmallow import Schema, fields, validate, pre_load, EXCLUDE


class DepartmentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=150, error="Department name must be 2-150 characters."),
        error_messages={"required": "Department name is required."},
    )
    code = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=20, error="Department code must be 2-20 characters."),
        error_messages={"required": "Department code is required."},
    )
    description = fields.Str(load_default=None)
    is_active = fields.Bool(load_default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    labs_count = fields.Int(dump_only=True)
    users_count = fields.Int(dump_only=True)

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict):
            if "name" in data and isinstance(data["name"], str):
                data["name"] = data["name"].strip()
            if "code" in data and isinstance(data["code"], str):
                data["code"] = data["code"].strip().upper()
        return data


class UpdateDepartmentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(
        validate=validate.Length(min=2, max=150, error="Department name must be 2-150 characters.")
    )
    code = fields.Str(
        validate=validate.Length(min=2, max=20, error="Department code must be 2-20 characters.")
    )
    description = fields.Str()
    is_active = fields.Bool()

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict):
            if "name" in data and isinstance(data["name"], str):
                data["name"] = data["name"].strip()
            if "code" in data and isinstance(data["code"], str):
                data["code"] = data["code"].strip().upper()
        return data

