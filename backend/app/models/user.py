"""
app/models/user.py
──────────────────
SQLAlchemy ORM model for the `users` table.

Roles
-----
  student       – default role assigned on self-registration
  lab_incharge  – manages a specific laboratory
  super_admin   – full platform access

Password hashing
----------------
  Uses the `bcrypt` library directly (not Werkzeug) for OWASP-recommended
  Adaptive hashing.  Passwords are NEVER stored in plain text.
"""

import secrets
import hashlib
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

# ── Role enumeration ──────────────────────────────────────────────────────────
ROLE_STUDENT = "student"
ROLE_LAB_INCHARGE = "lab_incharge"
ROLE_SUPER_ADMIN = "super_admin"

VALID_ROLES = (ROLE_STUDENT, ROLE_LAB_INCHARGE, ROLE_SUPER_ADMIN)


class User(db.Model):
    """
    Represents an authenticated user of the LabLoop platform.

    All three user types (student, lab_incharge, super_admin) share this
    table; the `role` column differentiates access levels.
    """

    __tablename__ = "users"

    # ── Primary key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Department ────────────────────────────────────────────────────────────
    department_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # ── Identity ──────────────────────────────────────────────────────────────
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # ── Role & profile ────────────────────────────────────────────────────────
    role: Mapped[str] = mapped_column(
        Enum(ROLE_STUDENT, ROLE_LAB_INCHARGE, ROLE_SUPER_ADMIN, name="user_role"),
        nullable=False,
        default=ROLE_STUDENT,
    )
    roll_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    admission_year: Mapped[str] = mapped_column(String(10), nullable=True)
    department_code: Mapped[str] = mapped_column(String(20), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    profile_image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # ── Account state ─────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    otp_code: Mapped[str] = mapped_column(String(100), nullable=True)
    otp_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Password-reset flow ───────────────────────────────────────────────────
    password_reset_token: Mapped[str] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Audit timestamps ──────────────────────────────────────────────────────
    last_login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    department = relationship("Department", back_populates="users", lazy="select")
    lab_assignments = relationship("LabAssignment", back_populates="user", cascade="all, delete-orphan", lazy="select")

    # ── Password helpers ──────────────────────────────────────────────────────

    def set_password(self, password: str) -> None:
        """
        Hash *password* with bcrypt and store the result in `password_hash`.

        Parameters
        ----------
        password : str
            Plain-text password supplied by the user.
        """
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), salt
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """
        Verify *password* against the stored bcrypt hash.

        Parameters
        ----------
        password : str
            Plain-text password to verify.

        Returns
        -------
        bool
            True if the password matches, False otherwise.
        """
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    # ── Password-reset helpers ────────────────────────────────────────────────

    def generate_reset_token(self) -> str:
        """
        Generate a secure URL-safe reset token, store its SHA-256 hash in the
        model, and return the **raw** token (to be sent to the user).

        Returns
        -------
        str
            The raw (unhashed) token to include in the reset URL.
        """
        from datetime import timedelta

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        self.password_reset_token = token_hash
        self.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        return raw_token

    # ── OTP Email Verification Helpers ────────────────────────────────────────

    def set_otp(self, code: str, minutes: int = 15) -> None:
        """Store SHA-256 hash of OTP code with expiration."""
        from datetime import timedelta
        self.otp_code = hashlib.sha256(code.strip().encode("utf-8")).hexdigest()
        self.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    def verify_otp(self, code: str) -> bool:
        """Verify supplied OTP code against stored hash and check expiration."""
        if not self.otp_code or not self.otp_expires_at:
            return False
        # Check expiry
        now = datetime.now(timezone.utc)
        expires = self.otp_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if now > expires:
            return False
        code_hash = hashlib.sha256(code.strip().encode("utf-8")).hexdigest()
        return secrets.compare_digest(self.otp_code, code_hash)

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Return a JSON-safe representation of the user.

        Sensitive fields (password_hash, reset tokens) are intentionally
        excluded.
        """
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "roll_number": self.roll_number,
            "admission_year": self.admission_year,
            "department_code": self.department_code,
            "phone": self.phone,
            "profile_image_url": self.profile_image_url,
            "department_id": self.department_id,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "last_login_at": (
                self.last_login_at.isoformat() if self.last_login_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    # ── Dunder ────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"
