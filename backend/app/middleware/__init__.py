"""
app/middleware/__init__.py
──────────────────────────
Re-exports middleware decorators for convenient imports.
"""

from app.middleware.role_required import role_required, get_current_user  # noqa: F401

__all__ = ["role_required", "get_current_user"]
