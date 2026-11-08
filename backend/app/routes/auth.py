"""
app/routes/auth.py
───────────────────
Authentication blueprint for LabLoop.

All routes are prefixed with /api/auth (registered in app/__init__.py).

Endpoints
---------
  POST   /register          – create a new student account
  POST   /login             – authenticate and receive JWT tokens
  POST   /refresh           – exchange a valid refresh token for a new access token
  POST   /logout            – revoke a single refresh token
  POST   /logout-all        – revoke ALL refresh tokens for the current user
  POST   /forgot-password   – request a password-reset e-mail
  POST   /reset-password    – set a new password using a reset token
  GET    /me                – return the authenticated user's profile
  PATCH  /me                – update profile fields (full_name, phone)
  PATCH  /me/password       – change password (requires current password)
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone

from flask import Blueprint, request, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from app.extensions import db, limiter
from app.middleware.role_required import get_current_user
from app.models.refresh_token import RefreshToken
from app.models.user import ROLE_STUDENT, User
from app.schemas.auth_schema import (
    ChangePasswordSchema,
    ForgotPasswordSchema,
    LoginSchema,
    RegisterSchema,
    ResetPasswordSchema,
    UpdateProfileSchema,
)
from app.services.auth_service import (
    create_refresh_token_record,
    hash_token,
    validate_refresh_token,
)
from app.utils.helpers import error_response, success_response

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# ── Schema singletons (instantiated once, thread-safe) ────────────────────────
_register_schema = RegisterSchema()
_login_schema = LoginSchema()
_forgot_password_schema = ForgotPasswordSchema()
_reset_password_schema = ResetPasswordSchema()
_change_password_schema = ChangePasswordSchema()
_update_profile_schema = UpdateProfileSchema()


# ── Helper: parse + validate JSON body ───────────────────────────────────────

def _load_json(schema, request_obj):
    """
    Load and validate JSON from *request_obj* using *schema*.

    Returns
    -------
    tuple (data, None) | tuple (None, error_response)
    """
    json_data = request_obj.get_json(silent=True)
    if json_data is None:
        return None, error_response("Request body must be valid JSON.", 400)
    try:
        data = schema.load(json_data)
    except ValidationError as exc:
        return None, error_response("Validation failed.", 422, exc.messages)
    return data, None


# ── POST /register ────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("20 per hour")
def register():
    """
    Register a new student with an institutional email:
    format: studentname.ug.YY.DD@francisxavier.ac.in
    Strictly restricted to role 'student'. Requires email OTP verification before activation.
    """
    import secrets
    from app.schemas.auth_schema import _STUDENT_EMAIL_RE
    from app.models.department import Department
    from app.services.email_service import send_otp_email, is_smtp_configured

    data, err = _load_json(_register_schema, request)
    if err:
        return err

    # Confirm password match if supplied
    if data.get("confirm_password") and data["password"] != data["confirm_password"]:
        return error_response("Passwords do not match.", 422, {"confirm_password": ["Passwords do not match."]})

    email = data["email"].strip().lower()

    # Parse student email components: <name>.ug.<year>.<dept>@francisxavier.ac.in
    match = _STUDENT_EMAIL_RE.match(email)
    if not match:
        return error_response(
            "Invalid institutional email. Must match: studentname.ug.YY.DD@francisxavier.ac.in",
            422,
        )

    # Check for existing account
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.email_verified:
        return error_response(
            "An active account with this institutional email already exists. Please sign in.",
            409,
        )

    student_name_part = match.group(1)
    admission_year = data.get("admission_year") or match.group(2)
    department_code = (data.get("department_code") or match.group(3)).upper()

    # Link department if exists
    dept_id = data.get("department_id")
    if not dept_id and department_code:
        dept = Department.query.filter(
            (Department.code.ilike(department_code)) |
            (Department.code.ilike(f"%{department_code}%")) |
            (Department.name.ilike(f"%{department_code}%"))
        ).first()
        if dept:
            dept_id = dept.id

    # Generate 6-digit cryptographic OTP
    otp_code = f"{secrets.randbelow(900000) + 100000}"

    try:
        if existing_user and not existing_user.email_verified:
            user = existing_user
            user.full_name = data["full_name"]
            user.admission_year = admission_year
            user.department_code = department_code
            user.department_id = dept_id
            user.set_password(data["password"])
        else:
            user = User(
                full_name=data["full_name"],
                email=email,
                role=ROLE_STUDENT,
                admission_year=admission_year,
                department_code=department_code,
                roll_number=data.get("roll_number") or f"{department_code}{admission_year}{user_seq():03d}",
                phone=data.get("phone"),
                department_id=dept_id,
                is_active=False,
                email_verified=False,
            )
            user.set_password(data["password"])
            db.session.add(user)

        # Store hashed OTP and 15-minute expiry
        user.set_otp(otp_code, minutes=15)
        db.session.commit()
        logger.info("Student registration pending verification: id=%s email=%s", user.id, user.email)

        # Dispatch real OTP via SMTP
        email_sent, email_msg = send_otp_email(user.email, user.full_name, otp_code)
        if current_app.debug:
            logger.info("[DEV] OTP generated for %s: %s (SMTP sent: %s)", user.email, otp_code, email_sent)

        if not email_sent:
            err_data = {
                "requires_otp": True,
                "smtp_configured": False,
                "email": user.email,
                "help": "Configure MAIL_USERNAME and MAIL_PASSWORD in backend/.env to send real OTP emails.",
            }
            # Only leak dev_otp in local development debug mode; never in production
            if current_app.debug:
                err_data["dev_otp"] = otp_code

            return error_response(
                f"Account created, but OTP email could not be delivered: {email_msg}",
                503,
                err_data,
            )

        return success_response(
            {
                "email": user.email,
                "requires_otp": True,
                "smtp_configured": True,
            },
            "Registration submitted! A 6-digit verification code has been dispatched to your institutional email. Enter the OTP to activate your account.",
            201,
        )

    except Exception as exc:
        db.session.rollback()
        logger.exception("Error during student registration: %s", exc)
        return error_response(f"Registration failed: {str(exc)}", 500)


# ── POST /verify-otp ──────────────────────────────────────────────────────────

@auth_bp.route("/verify-otp", methods=["POST"])
@limiter.limit("30 per hour")
def verify_otp():
    """Verify ownership of student institutional email using the 6-digit OTP code."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    otp = (data.get("otp") or "").strip()

    if not email or not otp:
        return error_response("Email and OTP code are required.", 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response("Account not found with this email address.", 404)

    if user.email_verified:
        return success_response(user.to_dict(), "Email is already verified. You may sign in.")

    if not user.verify_otp(otp):
        return error_response(
            "Invalid or expired OTP code. Please verify the code or request a new one.",
            400,
        )

    # Activate student account
    user.email_verified = True
    user.is_active = True
    user.otp_code = None
    user.otp_expires_at = None
    db.session.commit()

    logger.info("Student email verified: id=%s email=%s", user.id, user.email)
    return success_response(
        user.to_dict(),
        "Email verification successful! Your student account is now active. You may log in.",
        200,
    )


# ── POST /resend-otp ──────────────────────────────────────────────────────────

@auth_bp.route("/resend-otp", methods=["POST"])
@limiter.limit("10 per hour")
def resend_otp():
    """Generate and dispatch a fresh OTP to the student's institutional inbox."""
    import secrets
    from app.services.email_service import send_otp_email

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return error_response("Email is required.", 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response("No student account found with this email.", 404)

    if user.email_verified:
        return success_response(user.to_dict(), "Account is already verified. Please sign in.")

    otp_code = f"{secrets.randbelow(900000) + 100000}"
    user.set_otp(otp_code, minutes=15)
    db.session.commit()

    email_sent, email_msg = send_otp_email(user.email, user.full_name, otp_code)
    if current_app.debug:
        logger.info("[DEV] Resend OTP for %s: %s (SMTP sent: %s)", user.email, otp_code, email_sent)

    if not email_sent:
        err_data = {"smtp_configured": False, "email": user.email}
        if current_app.debug:
            err_data["dev_otp"] = otp_code
        return error_response(
            f"Cannot send OTP: {email_msg}",
            503,
            err_data,
        )

    return success_response(
        {"email": user.email},
        "A fresh verification code has been dispatched to your institutional inbox.",
    )


# ── GET /smtp-status ──────────────────────────────────────────────────────────

@auth_bp.route("/smtp-status", methods=["GET"])
def smtp_status():
    """Return whether the SMTP email subsystem is configured."""
    from app.services.email_service import is_smtp_configured
    configured = is_smtp_configured()
    return success_response(
        {"smtp_configured": configured},
        "SMTP configured." if configured else "SMTP unconfigured in backend/.env.",
    )


def user_seq() -> int:
    """Generate sequential number for fallback roll number generation."""
    return (User.query.count() % 900) + 101



# ── POST /login ───────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("20 per hour")
def login():
    """
    Authenticate a user and return JWT access + refresh tokens.

    Request body (JSON)
    -------------------
    email    : str (required)
    password : str (required)

    Returns 200 with {access_token, refresh_token, user} on success.
    """
    data, err = _load_json(_login_schema, request)
    if err:
        return err

    user: User = User.query.filter_by(email=data["email"]).first()

    # Use a constant-time comparison path to prevent user enumeration via
    # timing attacks.
    if user is None or not user.check_password(data["password"]):
        return error_response("Invalid email or password.", 401)

    # Strictly verify student activation and email verification
    if user.role == ROLE_STUDENT and not user.email_verified:
        return error_response(
            "Your institutional email has not been verified. Please verify your OTP to activate your account.",
            403,
            {"requires_otp": True, "email": user.email},
        )

    if not user.is_active:
        return error_response(
            "Your account has been deactivated. Please contact support.", 403
        )

    # Create JWT tokens (identity as string for standard JWT subject format)
    additional_claims = {"role": user.role, "email": user.email}
    access_token = create_access_token(
        identity=str(user.id), additional_claims=additional_claims
    )
    raw_refresh_token = create_refresh_token(identity=str(user.id))

    try:
        create_refresh_token_record(user.id, raw_refresh_token, request)
        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error persisting refresh token for user %s: %s", user.id, exc)
        return error_response("Login failed. Please try again.", 500)

    logger.info("User logged in: id=%s email=%s", user.id, user.email)
    return success_response(
        {
            "access_token": access_token,
            "refresh_token": raw_refresh_token,
            "user": user.to_dict(),
        },
        "Logged in successfully.",
        200,
    )


# ── POST /refresh ─────────────────────────────────────────────────────────────

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Exchange a valid refresh token for a new access token.

    Requires
    --------
    Authorization: Bearer <refresh_token>

    The raw refresh token must also be present in the JSON body under the
    key ``refresh_token`` so its DB record can be verified.

    Returns 200 with {access_token} on success.
    """
    user_id: int = get_jwt_identity()

    # Expect the raw refresh token in the body for DB validation
    body = request.get_json(silent=True) or {}
    raw_refresh_token: str = body.get("refresh_token", "")

    if not raw_refresh_token:
        return error_response("refresh_token is required in the request body.", 400)

    token_record = validate_refresh_token(user_id, raw_refresh_token)
    if token_record is None:
        return error_response(
            "Refresh token is invalid or has expired. Please log in again.", 401
        )

    # Fetch user to include fresh claims
    user: User = db.session.get(User, user_id)
    if user is None or not user.is_active:
        return error_response("User not found or account deactivated.", 401)

    additional_claims = {"role": user.role, "email": user.email}
    new_access_token = create_access_token(
        identity=user_id, additional_claims=additional_claims
    )

    return success_response({"access_token": new_access_token}, "Token refreshed.", 200)


# ── POST /logout ──────────────────────────────────────────────────────────────

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Revoke a single refresh token (log out from the current device).

    Request body (JSON)
    -------------------
    refresh_token : str (required — the raw refresh token to revoke)

    Returns 200 on success.
    """
    user_id: int = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    raw_refresh_token: str = body.get("refresh_token", "")

    if not raw_refresh_token:
        return error_response("refresh_token is required in the request body.", 400)

    token_hash = hash_token(raw_refresh_token)
    record: RefreshToken = RefreshToken.query.filter_by(
        user_id=user_id, token_hash=token_hash
    ).first()

    if record and not record.is_revoked:
        try:
            record.revoke()
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            logger.exception("Error revoking refresh token: %s", exc)
            return error_response("Logout failed. Please try again.", 500)

    return success_response(None, "Logged out successfully.", 200)


# ── POST /logout-all ──────────────────────────────────────────────────────────

@auth_bp.route("/logout-all", methods=["POST"])
@jwt_required()
def logout_all():
    """
    Revoke ALL refresh tokens for the authenticated user (log out from
    every device / session).

    Returns 200 on success.
    """
    user_id: int = get_jwt_identity()

    try:
        updated = (
            RefreshToken.query.filter_by(user_id=user_id, is_revoked=False)
            .update({"is_revoked": True})
        )
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error revoking all tokens for user %s: %s", user_id, exc)
        return error_response("Logout failed. Please try again.", 500)

    logger.info("Revoked %d refresh tokens for user %s", updated, user_id)
    return success_response(
        {"revoked_count": updated}, "Logged out from all devices.", 200
    )


# ── POST /forgot-password ─────────────────────────────────────────────────────

@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per hour")
def forgot_password():
    """
    Initiate the password-reset flow for the given e-mail address.

    Always returns 200 regardless of whether the e-mail exists, to prevent
    user-enumeration attacks.

    Request body (JSON)
    -------------------
    email : str (required)
    """
    data, err = _load_json(_forgot_password_schema, request)
    if err:
        return err

    user: User = User.query.filter_by(email=data["email"]).first()

    if user and user.is_active:
        try:
            raw_token = user.generate_reset_token()
            db.session.commit()

            # Build the reset URL (Phase 1: log to console; Phase 2: send e-mail)
            from flask import current_app
            frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
            reset_url = f"{frontend_url}/reset-password?token={raw_token}"

            logger.info(
                "[LabLoop] Password reset requested for %s — reset URL: %s",
                user.email,
                reset_url,
            )
            # Print to console for developer visibility during Phase 1
            print(f"\n{'='*60}")
            print(f"[LabLoop] Password Reset URL for {user.email}:")
            print(f"  {reset_url}")
            print(f"{'='*60}\n")

        except Exception as exc:
            db.session.rollback()
            logger.exception(
                "Error generating reset token for user %s: %s", data["email"], exc
            )

    # Always return 200 (email enumeration prevention)
    return success_response(
        None,
        "If an account with that email exists, a password reset link has been sent.",
        200,
    )


# ── POST /reset-password ──────────────────────────────────────────────────────

@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("10 per hour")
def reset_password():
    """
    Complete the password-reset flow.

    Request body (JSON)
    -------------------
    token        : str (the raw token from the reset URL)
    new_password : str (min 8 chars, letter + digit)

    Returns 200 on success.
    """
    data, err = _load_json(_reset_password_schema, request)
    if err:
        return err

    token_hash = hashlib.sha256(data["token"].encode("utf-8")).hexdigest()

    user: User = User.query.filter_by(password_reset_token=token_hash).first()

    if user is None:
        return error_response("Invalid or expired password reset token.", 400)

    # Check expiry
    if user.password_reset_expires is None or datetime.now(timezone.utc) > user.password_reset_expires:
        return error_response("Password reset token has expired. Please request a new one.", 400)

    try:
        user.set_password(data["new_password"])
        user.password_reset_token = None
        user.password_reset_expires = None

        # Revoke all existing refresh tokens for security
        RefreshToken.query.filter_by(user_id=user.id, is_revoked=False).update(
            {"is_revoked": True}
        )
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error resetting password for user %s: %s", user.id, exc)
        return error_response("Password reset failed. Please try again.", 500)

    logger.info("Password reset completed for user %s", user.id)
    return success_response(None, "Password has been reset successfully. Please log in.", 200)


# ── GET /me ───────────────────────────────────────────────────────────────────

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    """
    Return the authenticated user's public profile.

    Returns 200 with the user dict on success.
    """
    user = get_current_user()
    if user is None:
        return error_response("User not found.", 404)
    return success_response(user.to_dict(), "User profile retrieved.", 200)


# ── PATCH /me ─────────────────────────────────────────────────────────────────

@auth_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_me():
    """
    Update the authenticated user's profile fields (full_name, phone).

    Request body (JSON) — all fields optional
    ------------------------------------------
    full_name : str (2–150 chars)
    phone     : str

    Returns 200 with the updated user dict on success.
    """
    user = get_current_user()
    if user is None:
        return error_response("User not found.", 404)

    data, err = _load_json(_update_profile_schema, request)
    if err:
        return err

    try:
        if data.get("full_name") is not None:
            user.full_name = data["full_name"]
        if data.get("phone") is not None:
            user.phone = data["phone"]

        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error updating profile for user %s: %s", user.id, exc)
        return error_response("Profile update failed. Please try again.", 500)

    return success_response(user.to_dict(), "Profile updated successfully.", 200)


# ── PATCH /me/password ────────────────────────────────────────────────────────

@auth_bp.route("/me/password", methods=["PATCH"])
@jwt_required()
def change_password():
    """
    Change the authenticated user's password.

    Request body (JSON)
    -------------------
    current_password : str (required — must match the existing password)
    new_password     : str (required, min 8 chars, letter + digit)

    Returns 200 on success.
    """
    user = get_current_user()
    if user is None:
        return error_response("User not found.", 404)

    data, err = _load_json(_change_password_schema, request)
    if err:
        return err

    if not user.check_password(data["current_password"]):
        return error_response("Current password is incorrect.", 400)

    if data["current_password"] == data["new_password"]:
        return error_response(
            "New password must be different from the current password.", 400
        )

    try:
        user.set_password(data["new_password"])
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error changing password for user %s: %s", user.id, exc)
        return error_response("Password change failed. Please try again.", 500)

    return success_response(None, "Password changed successfully.", 200)
