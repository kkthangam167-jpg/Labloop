"""
app/models/refresh_token.py
────────────────────────────
SQLAlchemy ORM model for the `refresh_tokens` table.

Security design
---------------
  • The raw JWT refresh token is NEVER stored in the database.
  • A SHA-256 hex digest of the raw token is stored instead.
  • On every `/api/auth/refresh` or `/api/auth/logout` call the incoming
    raw token is hashed and looked up — matching the stored digest.
  • Tokens can be revoked individually (logout) or in bulk (logout-all /
    password-reset).
"""

import hashlib
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class RefreshToken(db.Model):
    """
    Persisted refresh-token record linked to a specific user.

    One user may have multiple active refresh tokens (one per device /
    browser session).  Each record stores a SHA-256 hash of the raw token
    so that the plaintext value is never at rest.
    """

    __tablename__ = "refresh_tokens"

    # ── Primary key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Owner ─────────────────────────────────────────────────────────────────
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Token storage (hashed) ────────────────────────────────────────────────
    token_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )

    # ── Context metadata ──────────────────────────────────────────────────────
    device_info: Mapped[str] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)

    # ── State ─────────────────────────────────────────────────────────────────
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # ── Audit ─────────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationship ──────────────────────────────────────────────────────────
    user = relationship("User", back_populates="refresh_tokens")

    # ── Business logic ────────────────────────────────────────────────────────

    def is_valid(self) -> bool:
        """
        Return True if the token is neither revoked nor past its expiry.
        """
        if self.is_revoked:
            return False
        expires_at = self.expires_at
        if expires_at is None:
            return False
        if expires_at.tzinfo is not None:
            now = datetime.now(timezone.utc)
        else:
            now = datetime.utcnow()
        return now < expires_at

    def revoke(self) -> None:
        """Mark this token as revoked (does not commit the session)."""
        self.is_revoked = True

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a JSON-safe representation (token_hash is excluded)."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_info": self.device_info,
            "ip_address": self.ip_address,
            "is_revoked": self.is_revoked,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_valid": self.is_valid(),
        }

    # ── Dunder ────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"<RefreshToken id={self.id} user_id={self.user_id} "
            f"revoked={self.is_revoked}>"
        )
