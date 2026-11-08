"""
app/schemas/__init__.py
────────────────────────
Convenience re-exports for all Marshmallow schemas.
"""

from app.schemas.auth_schema import (  # noqa: F401
    RegisterSchema,
    LoginSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    ChangePasswordSchema,
    UpdateProfileSchema,
)

__all__ = [
    "RegisterSchema",
    "LoginSchema",
    "ForgotPasswordSchema",
    "ResetPasswordSchema",
    "ChangePasswordSchema",
    "UpdateProfileSchema",
]
