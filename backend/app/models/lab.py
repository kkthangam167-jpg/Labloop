"""
app/models/lab.py
─────────────────
Lab and LabAssignment models for LabLoop.
"""

from __future__ import annotations

from datetime import datetime, timezone
from app.extensions import db


class Lab(db.Model):
    __tablename__ = "labs"

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(
        db.Integer, db.ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = db.Column(db.String(150), nullable=False, index=True)
    location = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    capacity = db.Column(db.Integer, default=30, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    department = db.relationship("Department", back_populates="labs")
    assignments = db.relationship(
        "LabAssignment", back_populates="lab", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Lab {self.id}: {self.name}>"

    def to_dict(self, include_department: bool = True, include_incharges: bool = True) -> dict:
        data = {
            "id": self.id,
            "department_id": self.department_id,
            "name": self.name,
            "location": self.location,
            "description": self.description,
            "capacity": self.capacity,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_department and self.department:
            data["department"] = {
                "id": self.department.id,
                "name": self.department.name,
                "code": self.department.code,
            }
        if include_incharges:
            active_assignments = [a for a in self.assignments if a.revoked_at is None]
            data["incharges"] = [
                {
                    "assignment_id": a.id,
                    "user_id": a.user_id,
                    "full_name": a.user.full_name if a.user else None,
                    "email": a.user.email if a.user else None,
                    "is_primary": a.is_primary,
                    "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
                }
                for a in active_assignments
            ]
        return data


class LabAssignment(db.Model):
    __tablename__ = "lab_assignments"

    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(
        db.Integer, db.ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    assigned_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    revoked_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    lab = db.relationship("Lab", back_populates="assignments")
    user = db.relationship("User", back_populates="lab_assignments")

    def __repr__(self) -> str:
        return f"<LabAssignment user_id={self.user_id} lab_id={self.lab_id}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lab_id": self.lab_id,
            "user_id": self.user_id,
            "is_primary": self.is_primary,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "user_name": self.user.full_name if self.user else None,
            "lab_name": self.lab.name if self.lab else None,
        }

