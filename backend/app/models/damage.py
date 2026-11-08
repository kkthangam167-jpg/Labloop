"""
app/models/damage.py
────────────────────
DamageReport and DamageImage models for LabLoop.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from app.extensions import db


SEVERITY_MINOR = "minor"
SEVERITY_MODERATE = "moderate"
SEVERITY_SEVERE = "severe"
SEVERITY_CRITICAL = "critical"

STATUS_OPEN = "open"
STATUS_UNDER_REVIEW = "under_review"
STATUS_RESOLVED = "resolved"
STATUS_REJECTED = "rejected"

SEVERITY_LEVELS = [
    SEVERITY_MINOR,
    SEVERITY_MODERATE,
    SEVERITY_SEVERE,
    SEVERITY_CRITICAL,
]

DAMAGE_STATUSES = [
    STATUS_OPEN,
    STATUS_UNDER_REVIEW,
    STATUS_RESOLVED,
    STATUS_REJECTED,
]


class DamageReport(db.Model):
    """Incident report for broken or malfunctioning equipment."""

    __tablename__ = "damage_reports"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False, index=True)
    reported_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    severity = db.Column(db.String(30), default=SEVERITY_MODERATE, nullable=False)
    status = db.Column(db.String(30), default=STATUS_OPEN, nullable=False, index=True)

    affects_availability = db.Column(db.Boolean, default=False, nullable=False)
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)

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
    equipment = db.relationship("Equipment", backref=db.backref("damage_reports", lazy="dynamic"))
    reporter = db.relationship("User", foreign_keys=[reported_by], backref=db.backref("damage_reports_filed", lazy="dynamic"))
    resolver = db.relationship("User", foreign_keys=[resolved_by])
    booking = db.relationship("Booking", backref=db.backref("damage_reports", lazy="dynamic"))
    images = db.relationship("DamageImage", back_populates="report", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self, include_equipment: bool = True, include_reporter: bool = True) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "reported_by": self.reported_by,
            "booking_id": self.booking_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "affects_availability": self.affects_availability,
            "resolution_notes": self.resolution_notes,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "images": [img.image_url for img in self.images],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_equipment and self.equipment:
            data["equipment"] = {
                "id": self.equipment.id,
                "name": self.equipment.name,
                "serial_number": self.equipment.serial_number,
                "lab_id": self.equipment.lab_id,
                "lab_name": self.equipment.lab.name if self.equipment.lab else None,
            }
        if include_reporter and self.reporter:
            data["reporter"] = {
                "id": self.reporter.id,
                "full_name": self.reporter.full_name,
                "email": self.reporter.email,
                "roll_number": self.reporter.roll_number,
            }
        return data


class DamageImage(db.Model):
    """Photo evidence attached to an equipment damage incident."""

    __tablename__ = "damage_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_id = db.Column(db.Integer, db.ForeignKey("damage_reports.id"), nullable=False, index=True)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    report = db.relationship("DamageReport", back_populates="images")

