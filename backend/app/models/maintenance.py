"""
app/models/maintenance.py
─────────────────────────
MaintenanceLog model for LabLoop preventive and corrective maintenance.
"""

from __future__ import annotations

from datetime import datetime, timezone, date
from typing import Optional, Dict, Any

from app.extensions import db


TYPE_SCHEDULED = "scheduled"
TYPE_CORRECTIVE = "corrective"
TYPE_INSPECTION = "inspection"
TYPE_CALIBRATION = "calibration"

STATUS_SCHEDULED = "scheduled"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"

MAINTENANCE_TYPES = [
    TYPE_SCHEDULED,
    TYPE_CORRECTIVE,
    TYPE_INSPECTION,
    TYPE_CALIBRATION,
]

MAINTENANCE_STATUSES = [
    STATUS_SCHEDULED,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
]


class MaintenanceLog(db.Model):
    """Maintenance record for equipment servicing, calibration, and repairs."""

    __tablename__ = "maintenance_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False, index=True)
    logged_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    maintenance_type = db.Column(db.String(30), default=TYPE_SCHEDULED, nullable=False)
    status = db.Column(db.String(30), default=STATUS_SCHEDULED, nullable=False, index=True)

    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    completed_date = db.Column(db.Date, nullable=True)

    cost = db.Column(db.Numeric(10, 2), nullable=True)
    performed_by_vendor = db.Column(db.String(150), nullable=True)
    attachments_json = db.Column(db.Text, nullable=True)

    send_alert = db.Column(db.Boolean, default=True, nullable=False)
    alert_sent_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    equipment = db.relationship("Equipment", backref=db.backref("maintenance_logs", lazy="dynamic"))
    technician = db.relationship("User", foreign_keys=[logged_by])

    def to_dict(self, include_equipment: bool = True) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "logged_by": self.logged_by,
            "title": self.title,
            "description": self.description,
            "maintenance_type": self.maintenance_type,
            "status": self.status,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "cost": float(self.cost) if self.cost is not None else None,
            "performed_by_vendor": self.performed_by_vendor,
            "send_alert": self.send_alert,
            "alert_sent_at": self.alert_sent_at.isoformat() if self.alert_sent_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_equipment and self.equipment:
            data["equipment"] = {
                "id": self.equipment.id,
                "name": self.equipment.name,
                "serial_number": self.equipment.serial_number,
                "lab_id": self.equipment.lab_id,
            }
        return data

