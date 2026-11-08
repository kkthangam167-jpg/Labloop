"""
app/models/booking.py
─────────────────────
Booking model for LabLoop resource reservations.
"""

from __future__ import annotations

from datetime import datetime, timezone, date, time
from typing import Optional, Dict, Any

from app.extensions import db


STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"
STATUS_NO_SHOW = "no_show"

BOOKING_STATUSES = [
    STATUS_PENDING,
    STATUS_APPROVED,
    STATUS_REJECTED,
    STATUS_ACTIVE,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
    STATUS_NO_SHOW,
]


class Booking(db.Model):
    """Resource booking reservation record."""

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False, index=True)
    booked_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    cancelled_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    booking_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    purpose = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(30), default=STATUS_PENDING, nullable=False, index=True)

    rejection_reason = db.Column(db.String(500), nullable=True)
    cancellation_reason = db.Column(db.String(500), nullable=True)

    checkin_time = db.Column(db.DateTime(timezone=True), nullable=True)
    checkout_time = db.Column(db.DateTime(timezone=True), nullable=True)
    qr_checkin_verified = db.Column(db.Boolean, default=False, nullable=False)
    qr_checkout_verified = db.Column(db.Boolean, default=False, nullable=False)

    checkin_qr_token = db.Column(db.String(64), nullable=True)
    checkout_qr_token = db.Column(db.String(64), nullable=True)

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
    equipment = db.relationship("Equipment", backref=db.backref("bookings", lazy="dynamic"))
    user = db.relationship("User", foreign_keys=[booked_by], backref=db.backref("my_bookings", lazy="dynamic"))
    approver = db.relationship("User", foreign_keys=[approved_by])
    canceller = db.relationship("User", foreign_keys=[cancelled_by])

    def to_dict(self, include_equipment: bool = True, include_user: bool = True) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "booked_by": self.booked_by,
            "approved_by": self.approved_by,
            "cancelled_by": self.cancelled_by,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "start_time": self.start_time.strftime("%H:%M") if self.start_time else None,
            "end_time": self.end_time.strftime("%H:%M") if self.end_time else None,
            "purpose": self.purpose,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "cancellation_reason": self.cancellation_reason,
            "checkin_time": self.checkin_time.isoformat() if self.checkin_time else None,
            "checkout_time": self.checkout_time.isoformat() if self.checkout_time else None,
            "qr_checkin_verified": self.qr_checkin_verified,
            "qr_checkout_verified": self.qr_checkout_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_equipment and self.equipment:
            data["equipment"] = {
                "id": self.equipment.id,
                "name": self.equipment.name,
                "model_number": self.equipment.model_number,
                "location_in_lab": self.equipment.location_in_lab,
                "lab_id": self.equipment.lab_id,
                "lab_name": self.equipment.lab.name if self.equipment.lab else None,
                "lab_location": self.equipment.lab.location if self.equipment.lab else None,
            }
        if include_user and self.user:
            data["user"] = {
                "id": self.user.id,
                "full_name": self.user.full_name,
                "email": self.user.email,
                "roll_number": self.user.roll_number,
            }
        return data

