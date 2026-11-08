"""
app/middleware/role_required.py
────────────────────────────────
JWT-aware authorisation helpers for LabLoop route handlers.

Usage
-----
::

    from app.middleware.role_required import role_required, get_current_user

    # Restrict a route to lab incharge and super admin only
    @auth_bp.route('/admin-only')
    @jwt_required()
    @role_required('lab_incharge', 'super_admin')
    def admin_view():
        user = get_current_user()
        return success_response(user.to_dict())
"""

from __future__ import annotations

import functools
from typing import Callable, Optional

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.extensions import db
from app.models.user import User


# ── Role enforcement decorator ────────────────────────────────────────────────


def role_required(*roles: str) -> Callable:
    """
    View decorator that restricts access to users whose JWT ``role`` claim
    matches one of the specified *roles*.

    Must be applied **after** ``@jwt_required()`` so that the JWT has
    already been validated and ``get_jwt()`` returns the full claims dict.

    Parameters
    ----------
    *roles : str
        One or more role strings (e.g. ``'super_admin'``, ``'lab_incharge'``).

    Returns
    -------
    Callable
        The decorated view function, or a 403 JSON response if the caller's
        role is not in the allowed set.

    Example
    -------
    ::

        @bp.route('/protected')
        @jwt_required()
        @role_required('super_admin')
        def protected():
            ...
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role: str = claims.get("role", "")

            if user_role not in roles:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": (
                                "You do not have permission to access this resource."
                            ),
                            "error": "forbidden",
                            "required_roles": list(roles),
                            "your_role": user_role,
                        }
                    ),
                    403,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


# ── Current-user helper ───────────────────────────────────────────────────────


def get_current_user() -> Optional[User]:
    """
    Return the :class:`~app.models.user.User` ORM object for the identity
    encoded in the current request's JWT access token.

    Must be called inside a request context where ``@jwt_required()`` has
    already validated the token (i.e. inside a route handler or a function
    called from one).

    Returns
    -------
    User | None
        The matching :class:`User` instance, or ``None`` if no user with
        that primary-key exists in the database.

    Example
    -------
    ::

        @bp.route('/me')
        @jwt_required()
        def me():
            user = get_current_user()
            if user is None:
                return error_response('User not found.', 404)
            return success_response(user.to_dict())
    """
    user_id: int = get_jwt_identity()
    if user_id is None:
        return None
    return db.session.get(User, user_id)
