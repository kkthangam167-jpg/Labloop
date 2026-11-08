"""
app/schemas/auth_schema.py
──────────────────────────
Marshmallow validation schemas for all authentication-related endpoints.
Compatible with Marshmallow 4+.
"""

import re
from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validate,
    validates,
    pre_load,
    EXCLUDE,
)

_PASSWORD_MIN_LEN = 8
_PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


def _validate_password_complexity(password: str) -> None:
    if len(password) < _PASSWORD_MIN_LEN:
        raise ValidationError(
            f"Password must be at least {_PASSWORD_MIN_LEN} characters long."
        )
    if not re.search(r"[A-Za-z]", password):
        raise ValidationError("Password must contain at least one letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one number.")


_STUDENT_EMAIL_RE = re.compile(
    r"^([a-z0-9]+(?:\.[a-z0-9]+)*)\.ug\.(\d{2})\.([a-z]{2,})@francisxavier\.ac\.in$"
)
_YEAR_RE = re.compile(r"^\d{2}$")
_DEPT_CODE_RE = re.compile(r"^[A-Za-z]{2,10}$")

class RegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=150, error="Full name must be 2–150 characters."),
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
        load_only=True,
        error_messages={"required": "Password is required."},
    )
    confirm_password = fields.Str(load_only=True, load_default=None)
    admission_year = fields.Str(
        load_default=None,
        validate=validate.Length(equal=2, error="Admission year must be a 2-digit code (e.g., 25, 26)."),
    )
    department_code = fields.Str(
        load_default=None,
        validate=validate.Length(min=2, max=10, error="Department code must be 2–10 characters (e.g., CS, EC, AI, IT)."),
    )
    roll_number = fields.Str(
        load_default=None,
        validate=validate.Length(max=50, error="Roll number must not exceed 50 characters."),
    )
    phone = fields.Str(load_default=None)
    department_id = fields.Int(load_default=None)

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict):
            if "email" in data and isinstance(data["email"], str):
                data["email"] = data["email"].strip().lower()
            if "full_name" in data and isinstance(data["full_name"], str):
                data["full_name"] = data["full_name"].strip()
            if "admission_year" in data and isinstance(data["admission_year"], str):
                data["admission_year"] = data["admission_year"].strip()
            if "department_code" in data and isinstance(data["department_code"], str):
                data["department_code"] = data["department_code"].strip().upper()
        return data

    @validates("email")
    def validate_institutional_email(self, value, **kwargs):
        match = _STUDENT_EMAIL_RE.match(value)
        if not match:
            raise ValidationError(
                "Invalid institutional student email format. Must follow: "
                "studentname.ug.YY.DD@francisxavier.ac.in (e.g., priya.ug.25.cs@francisxavier.ac.in)"
            )

    @validates("admission_year")
    def validate_year(self, value, **kwargs):
        if value and not _YEAR_RE.match(value):
            raise ValidationError("Admission year must be exactly two digits (e.g., 25, 26).")

    @validates("department_code")
    def validate_dept(self, value, **kwargs):
        if value and not _DEPT_CODE_RE.match(value):
            raise ValidationError("Department code must be alphabetic (e.g., CS, EC, AI, IT, ME, EE).")

    @validates("password")
    def validate_password(self, value, **kwargs):
        _validate_password_complexity(value)

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        if value and not _PHONE_RE.match(value):
            raise ValidationError(
                "Phone number must be 7–20 digits and may include +, spaces, dashes, or parentheses."
            )


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email address is required.",
            "validator_failed": "Enter a valid email address.",
        },
    )
    password = fields.Str(
        required=True,
        load_only=True,
        error_messages={"required": "Password is required."},
    )

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict) and "email" in data and isinstance(data["email"], str):
            data["email"] = data["email"].strip().lower()
        return data


class ForgotPasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email address is required.",
            "validator_failed": "Enter a valid email address.",
        },
    )

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict) and "email" in data and isinstance(data["email"], str):
            data["email"] = data["email"].strip().lower()
        return data


class ResetPasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    token = fields.Str(
        required=True,
        error_messages={"required": "Reset token is required."},
    )
    new_password = fields.Str(
        required=True,
        load_only=True,
        error_messages={"required": "New password is required."},
    )

    @validates("new_password")
    def validate_new_password(self, value, **kwargs):
        _validate_password_complexity(value)


class ChangePasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    current_password = fields.Str(
        required=True,
        load_only=True,
        error_messages={"required": "Current password is required."},
    )
    new_password = fields.Str(
        required=True,
        load_only=True,
        error_messages={"required": "New password is required."},
    )

    @validates("new_password")
    def validate_new_password(self, value, **kwargs):
        _validate_password_complexity(value)


class UpdateProfileSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.Str(
        load_default=None,
        validate=validate.Length(min=2, max=150, error="Full name must be 2–150 characters."),
    )
    phone = fields.Str(load_default=None)

    @pre_load
    def process_input(self, data, **kwargs):
        if isinstance(data, dict) and "full_name" in data and isinstance(data["full_name"], str):
            data["full_name"] = data["full_name"].strip()
        return data

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        if value and not _PHONE_RE.match(value):
            raise ValidationError(
                "Phone number must be 7–20 digits and may include +, spaces, dashes, or parentheses."
            )
