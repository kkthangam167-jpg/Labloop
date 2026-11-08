"""
app/config.py
─────────────
Configuration classes for LabLoop.

Three environments are provided:
  • DevelopmentConfig  – local dev, debug on
  • ProductionConfig   – deployed server, debug off, stricter settings
  • TestingConfig      – unit / integration tests, in-memory SQLite

All inherit from BaseConfig which pulls values from environment variables
(loaded via python-dotenv so a .env file is sufficient during development).
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Explicitly locate backend directory and load .env
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env")
load_dotenv()  # also fallback to current working directory .env if present


class BaseConfig:
    """Shared configuration values for all environments."""

    # ── Flask core ───────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production-labloop-2026"
    )
    DEBUG: bool = False
    TESTING: bool = False

    # ── Database ─────────────────────────────────────────────────
    _raw_db_url: str = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/labloop_db"
    )
    # Normalize postgres:// to postgresql:// for SQLAlchemy 1.4+ compatibility
    if _raw_db_url and _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI: str = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False

    # ── JWT ──────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = os.environ.get(
        "JWT_SECRET_KEY", "jwt-secret-key-change-in-production-labloop-2026"
    )
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=7)
    JWT_TOKEN_LOCATION: list = ["headers"]
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: list = [
        u.strip() for u in os.environ.get("FRONTEND_URL", "http://localhost:5173").split(",") if u.strip()
    ]

    # ── Rate limiting ────────────────────────────────────────────
    RATELIMIT_DEFAULT: str = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URI: str = "memory://"
    RATELIMIT_STRATEGY: str = "fixed-window"

    # ── Mail (Flask-Mail) ────────────────────────────────────────
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS: bool = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL: bool = False
    MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER: str = os.environ.get(
        "MAIL_DEFAULT_SENDER", "LabLoop <noreply@labloop.app>"
    )

    # ── File uploads ─────────────────────────────────────────────
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH: int = int(
        os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)  # 16 MB
    )

    # ── Frontend URL (used in e-mail links) ──────────────────────
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:5173")


class DevelopmentConfig(BaseConfig):
    """Development environment – verbose, debug enabled."""

    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = True  # Log all SQL statements


class ProductionConfig(BaseConfig):
    """Production environment – debug off, secure defaults."""

    DEBUG: bool = False
    SQLALCHEMY_ECHO: bool = False

    # Tighten rate limits in production
    RATELIMIT_DEFAULT: str = "500 per day;100 per hour"


class TestingConfig(BaseConfig):
    """Testing environment – uses SQLite in-memory, CSRF/rate-limit disabled."""

    DEBUG: bool = True
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SQLALCHEMY_ECHO: bool = False

    # Disable rate-limiting during tests
    RATELIMIT_ENABLED: bool = False

    # Speed up bcrypt during tests
    BCRYPT_LOG_ROUNDS: int = 4

    # Short-lived tokens for test assertions
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(seconds=10)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(seconds=30)


# ── Registry ─────────────────────────────────────────────────────────────────
config_by_name: dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    # Default alias
    "default": DevelopmentConfig,
}
