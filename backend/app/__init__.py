"""
app/__init__.py
───────────────
Application factory for LabLoop.

Usage
-----
    from app import create_app
    app = create_app('development')   # or 'production', 'testing'
"""

import os
from flask import Flask, jsonify

from app.config import config_by_name
from app.extensions import db, migrate, jwt, cors, limiter, mail


def create_app(config_name: str = None) -> Flask:
    """
    Create and configure the Flask application.

    Parameters
    ----------
    config_name : str, optional
        One of 'development', 'production', 'testing'.
        Falls back to the FLASK_ENV environment variable, then 'development'.

    Returns
    -------
    Flask
        The fully configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=False)

    # ── Load configuration ────────────────────────────────────────────────────
    cfg_class = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(cfg_class)

    # ── Initialise extensions ─────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure CORS: in development allow local dev origins; in production use configured origins
    configured_origins = app.config.get("CORS_ORIGINS", [])
    if app.config.get("DEBUG") or config_name == "development":
        allowed_origins = [
            r"http://localhost:[0-9]+",
            r"http://127.0.0.1:[0-9]+",
            *configured_origins,
        ]
    else:
        allowed_origins = configured_origins if configured_origins else ["*"]

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": allowed_origins,
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            }
        },
        supports_credentials=True,
    )
    limiter.init_app(app)
    mail.init_app(app)

    # ── Register blueprints ───────────────────────────────────────────────────
    from app.routes.auth import auth_bp  # noqa: E402
    from app.routes.users import users_bp  # noqa: E402
    from app.routes.departments import departments_bp  # noqa: E402
    from app.routes.labs import labs_bp  # noqa: E402
    from app.routes.equipment import equipment_bp  # noqa: E402
    from app.routes.bookings import bookings_bp  # noqa: E402
    from app.routes.damage import damage_bp  # noqa: E402
    from app.routes.maintenance import maintenance_bp  # noqa: E402

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(departments_bp, url_prefix="/api/departments")
    app.register_blueprint(labs_bp, url_prefix="/api/labs")
    app.register_blueprint(equipment_bp, url_prefix="/api/equipment")
    app.register_blueprint(bookings_bp, url_prefix="/api/bookings")
    app.register_blueprint(damage_bp, url_prefix="/api/damage-reports")
    app.register_blueprint(maintenance_bp, url_prefix="/api/maintenance")

    # ── JWT callbacks ─────────────────────────────────────────────────────────
    _register_jwt_callbacks(jwt)

    # ── Ensure upload folder exists ───────────────────────────────────────────
    upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    return app


# ── JWT error / event callbacks ───────────────────────────────────────────────

def _register_jwt_callbacks(jwt_manager: object) -> None:
    """Attach all JWT event handlers to the given JWTManager instance."""

    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Token has expired. Please log in again.",
                    "error": "token_expired",
                }
            ),
            401,
        )

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error_string):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Invalid token. Please log in again.",
                    "error": "token_invalid",
                }
            ),
            401,
        )

    @jwt_manager.unauthorized_loader
    def missing_token_callback(error_string):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Authentication token is missing.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt_manager.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Token has been revoked. Please log in again.",
                    "error": "token_revoked",
                }
            ),
            401,
        )

    @jwt_manager.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Fresh token required.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )
