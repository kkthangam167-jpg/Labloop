"""
app/models/notification.py
──────────────────────────
In-app and email notification tracking for LabLoop.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.extensions import db


TYPE_BOOKING_UPDATE = "booking_update"
TYPE_DAMAGE_UPDATE = "damage_update"
TYPE_MAINTENANCE_ALERT = "maintenance_alert"
TYPE_SYSTEM = "system"
TYPE_RECOMMENDATION = "recommendation"

NOTIFICATION_TYPES = [
    TYPE_BOOKING_UPDATE,
    TYPE_DAMAGE_UPDATE,
    TYPE_MAINTENANCE_ALERT,
    TYPE_SYSTEM,
    TYPE_RECOMMENDATION,
]


class Notification(db.Model):
    """User in-app notifications and email dispatch tracking."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default=TYPE_SYSTEM, nullable=False)

    entity_type = db.Column(db.String(50), nullable=True)  # 'booking', 'equipment', 'damage_report', etc.
    entity_id = db.Column(db.Integer, nullable=True)

    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    email_sent = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    user = db.relationship("User", backref=db.backref("notifications", lazy="dynamic"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "is_read": self.is_read,
            "email_sent": self.email_sent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

