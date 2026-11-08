"""
app/schemas/user_schema.py
──────────────────────────
Marshmallow validation schemas for Admin User Management endpoints.
"""

from marshmallow import Schema, fields, validate, pre_load, EXCLUDE
from app.models.user import VALID_ROLES

_PASSWORD_MIN_LEN = 8


class AdminCreateUserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=150, error="Full name must be 2-150 characters."),
        error_messages={"required": "Full name is required."},
    )
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email address is required.",
            "validator_failed": "Enter a valid email address.",
        },
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=_PASSWORD_MIN_LEN, error=f"Password must be at least {_PASSWORD_MIN_LEN} characters."),
        error_messages={"required": "Password is required."},
    )
    role = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_ROLES, error=f"Role must be one of: {', '.join(VALID_ROLES)}"),
        error_messages={"required": "Role is required."},
    )
    roll_number = fields.Str(load_default=None)
    admission_year = fields.Str(load_default=None)
    department_code = fields.Str(load_default=None)
    phone = fields.Str(load_default=None)
    department_id = fields.Int(load_default=None)
    is_active = fields.Bool(load_default=True)

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict):
            if "email" in data and isinstance(data["email"], str):
                data["email"] = data["email"].strip().lower()
            if "full_name" in data and isinstance(data["full_name"], str):
                data["full_name"] = data["full_name"].strip()
            if "roll_number" in data and isinstance(data["roll_number"], str):
                data["roll_number"] = data["roll_number"].strip().upper()
        return data


class AdminUpdateUserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.Str(
        validate=validate.Length(min=2, max=150, error="Full name must be 2-150 characters.")
    )
    email = fields.Email(error_messages={"validator_failed": "Enter a valid email address."})
    role = fields.Str(validate=validate.OneOf(VALID_ROLES, error=f"Role must be one of: {', '.join(VALID_ROLES)}"))
    roll_number = fields.Str()
    phone = fields.Str()
    department_id = fields.Int(allow_none=True)
    is_active = fields.Bool()
    password = fields.Str(
        validate=validate.Length(min=_PASSWORD_MIN_LEN, error=f"Password must be at least {_PASSWORD_MIN_LEN} characters.")
    )

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict):
            if "email" in data and isinstance(data["email"], str):
                data["email"] = data["email"].strip().lower()
            if "full_name" in data and isinstance(data["full_name"], str):
                data["full_name"] = data["full_name"].strip()
            if "roll_number" in data and isinstance(data["roll_number"], str):
                data["roll_number"] = data["roll_number"].strip().upper()
        return data

