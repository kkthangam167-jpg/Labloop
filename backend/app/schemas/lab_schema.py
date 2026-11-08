"""
app/schemas/lab_schema.py
─────────────────────────
Marshmallow validation schemas for Lab and LabAssignment endpoints.
"""

from marshmallow import Schema, fields, validate, pre_load, EXCLUDE


class LabSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    department_id = fields.Int(
        required=True,
        error_messages={"required": "department_id is required."},
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=150, error="Lab name must be 2-150 characters."),
        error_messages={"required": "Lab name is required."},
    )
    location = fields.Str(load_default=None)
    description = fields.Str(load_default=None)
    capacity = fields.Int(
        load_default=30,
        validate=validate.Range(min=1, max=1000, error="Capacity must be between 1 and 1000."),
    )
    is_active = fields.Bool(load_default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    department = fields.Dict(dump_only=True)
    incharges = fields.List(fields.Dict(), dump_only=True)

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict):
            if "name" in data and isinstance(data["name"], str):
                data["name"] = data["name"].strip()
            if "location" in data and isinstance(data["location"], str):
                data["location"] = data["location"].strip()
        return data


class UpdateLabSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    department_id = fields.Int()
    name = fields.Str(
        validate=validate.Length(min=2, max=150, error="Lab name must be 2-150 characters.")
    )
    location = fields.Str()
    description = fields.Str()
    capacity = fields.Int(
        validate=validate.Range(min=1, max=1000, error="Capacity must be between 1 and 1000.")
    )
    is_active = fields.Bool()

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict):
            if "name" in data and isinstance(data["name"], str):
                data["name"] = data["name"].strip()
            if "location" in data and isinstance(data["location"], str):
                data["location"] = data["location"].strip()
        return data


class AssignInchargeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    user_id = fields.Int(
        required=True,
        error_messages={"required": "user_id is required."},
    )
    is_primary = fields.Bool(load_default=False)

