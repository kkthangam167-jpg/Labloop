"""
app/models/equipment.py
───────────────────────
Equipment and EquipmentCategory models for LabLoop.
"""

from __future__ import annotations

import hmac
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.extensions import db


STATUS_AVAILABLE = "available"
STATUS_UNDER_MAINTENANCE = "under_maintenance"
STATUS_OUT_OF_ORDER = "out_of_order"
STATUS_RETIRED = "retired"

EQUIPMENT_STATUSES = [
    STATUS_AVAILABLE,
    STATUS_UNDER_MAINTENANCE,
    STATUS_OUT_OF_ORDER,
    STATUS_RETIRED,
]


class EquipmentCategory(db.Model):
    """Category taxonomy for equipment (e.g. Computing, Measurement, Prototyping)."""

    __tablename__ = "equipment_categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon_name = db.Column(db.String(50), nullable=True, default="Cpu")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    equipment = db.relationship("Equipment", back_populates="category", lazy="dynamic")

    def to_dict(self, include_count: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "icon_name": self.icon_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_count:
            data["equipment_count"] = self.equipment.filter_by(is_deleted=False).count()
        return data


class Equipment(db.Model):
    """Physical or digital equipment resource stationed within a laboratory."""

    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lab_id = db.Column(db.Integer, db.ForeignKey("labs.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("equipment_categories.id"), nullable=True, index=True)

    name = db.Column(db.String(150), nullable=False)
    model_number = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True, unique=True, index=True)
    manufacturer = db.Column(db.String(100), nullable=True)

    quantity_total = db.Column(db.Integer, default=1, nullable=False)
    quantity_available = db.Column(db.Integer, default=1, nullable=False)

    status = db.Column(db.String(30), default=STATUS_AVAILABLE, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    # QR tracking & security
    qr_code_token = db.Column(db.String(64), unique=True, nullable=True, index=True)
    qr_code_hmac = db.Column(db.String(128), nullable=True)
    qr_code_url = db.Column(db.String(500), nullable=True)

    # Purchasing & Maintenance
    purchase_cost = db.Column(db.Numeric(10, 2), nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    warranty_expiry = db.Column(db.Date, nullable=True)
    location_in_lab = db.Column(db.String(100), nullable=True)

    usage_count = db.Column(db.Integer, default=0, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)

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
    lab = db.relationship("Lab", backref=db.backref("equipment", lazy="dynamic"))
    category = db.relationship("EquipmentCategory", back_populates="equipment")

    def generate_qr(self, secret_key: str) -> str:
        """Generate a cryptographically random token and its HMAC signature."""
        token = secrets.token_hex(32)
        sig = hmac.new(secret_key.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()
        self.qr_code_token = token
        self.qr_code_hmac = sig
        return token

    def verify_qr(self, token: str, secret_key: str) -> bool:
        """Verify token and check constant-time HMAC equality."""
        if not self.qr_code_token or not self.qr_code_hmac:
            return False
        if not hmac.compare_digest(self.qr_code_token, token):
            return False
        expected_sig = hmac.new(secret_key.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(self.qr_code_hmac, expected_sig)

    def to_dict(self, include_lab: bool = True, include_category: bool = True) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "lab_id": self.lab_id,
            "category_id": self.category_id,
            "name": self.name,
            "model_number": self.model_number,
            "serial_number": self.serial_number,
            "manufacturer": self.manufacturer,
            "quantity_total": self.quantity_total,
            "quantity_available": self.quantity_available,
            "status": self.status,
            "description": self.description,
            "image_url": self.image_url,
            "qr_code_token": self.qr_code_token,
            "qr_code_url": self.qr_code_url,
            "purchase_cost": float(self.purchase_cost) if self.purchase_cost is not None else None,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "warranty_expiry": self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            "location_in_lab": self.location_in_lab,
            "usage_count": self.usage_count,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_lab and self.lab:
            data["lab"] = {
                "id": self.lab.id,
                "name": self.lab.name,
                "code": getattr(self.lab, "code", ""),
                "location": self.lab.location,
            }
        if include_category and self.category:
            data["category"] = {
                "id": self.category.id,
                "name": self.category.name,
                "slug": self.category.slug,
                "icon_name": self.category.icon_name,
            }
        return data

