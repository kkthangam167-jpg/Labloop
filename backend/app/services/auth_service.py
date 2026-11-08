"""
app/services/auth_service.py
─────────────────────────────
Business-logic helpers used by the authentication blueprint.

Keeping these functions in a service module (rather than inline in the
route handler) makes them independently unit-testable and reusable from
other parts of the application (e.g. admin commands, Celery tasks).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional

from flask import Request

from app.extensions import db
from app.models.refresh_token import RefreshToken


# ── Token hashing ─────────────────────────────────────────────────────────────


def hash_token(raw_token: str) -> str:
    """
    Return the SHA-256 hex digest of *raw_token*.

    This one-way hash is what gets stored in the database so that even if
    the `refresh_tokens` table is compromised, the attacker cannot replay
    the original tokens.

    Parameters
    ----------
    raw_token : str
        The raw JWT string (or any secret string) to hash.

    Returns
    -------
    str
        64-character lowercase hex string.
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


# ── Refresh-token DB record ───────────────────────────────────────────────────


def create_refresh_token_record(
    user_id: int,
    raw_token: str,
    request: Request,
    expires_delta: Optional[timedelta] = None,
) -> RefreshToken:
    """
    Create a new :class:`RefreshToken` database record and add it to the
    current SQLAlchemy session (without committing).

    Parameters
    ----------
    user_id : int
        Primary key of the owning :class:`~app.models.user.User`.
    raw_token : str
        The plain-text refresh token returned by Flask-JWT-Extended.
        Only its SHA-256 hash is persisted.
    request : flask.Request
        The current HTTP request; used to capture IP address and
        User-Agent device info.
    expires_delta : timedelta, optional
        How long until the token expires.  Defaults to 7 days when not
        provided.

    Returns
    -------
    RefreshToken
        The newly created (unsaved) model instance.
    """
    if expires_delta is None:
        expires_delta = timedelta(days=7)

    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + expires_delta

    # Capture context metadata for audit / revocation UX
    ip_address: str = (
        request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    )
    device_info: str = (request.headers.get("User-Agent") or "")[:500]

    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        device_info=device_info or None,
        ip_address=ip_address or None,
        expires_at=expires_at,
    )
    db.session.add(record)
    return record


# ── Refresh-token validation ──────────────────────────────────────────────────


def validate_refresh_token(
    user_id: int, raw_token: str
) -> Optional[RefreshToken]:
    """
    Look up the :class:`RefreshToken` record matching *raw_token* for the
    given *user_id* and confirm it is still valid.

    Parameters
    ----------
    user_id : int
        The user the token should belong to.
    raw_token : str
        The plain-text refresh token to validate.

    Returns
    -------
    RefreshToken | None
        The valid :class:`RefreshToken` instance, or ``None`` if the token
        was not found, has been revoked, or has expired.
    """
    token_hash = hash_token(raw_token)

    record: Optional[RefreshToken] = RefreshToken.query.filter_by(
        user_id=user_id,
        token_hash=token_hash,
    ).first()

    if record is None:
        return None

    if not record.is_valid():
        return None

    return record
