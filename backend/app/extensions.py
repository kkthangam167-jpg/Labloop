"""
app/extensions.py
─────────────────
Flask extension instances created here (not yet bound to an app).
The app factory (app/__init__.py) calls each extension's init_app()
so the same objects are importable throughout the codebase without
creating circular dependencies.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

# ── SQLAlchemy ORM ───────────────────────────────────────────────────────────
db = SQLAlchemy()

# ── Alembic / Flask-Migrate ──────────────────────────────────────────────────
migrate = Migrate()

# ── JWT authentication ───────────────────────────────────────────────────────
jwt = JWTManager()

# ── Cross-Origin Resource Sharing ────────────────────────────────────────────
cors = CORS()

# ── Request rate limiter ─────────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
)

# ── E-mail ───────────────────────────────────────────────────────────────────
mail = Mail()
