"""
app/models/department.py
─────────────────────────
Department model for LabLoop.
"""

from __future__ import annotations

from datetime import datetime, timezone
from app.extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
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
    labs = db.relationship("Lab", back_populates="department", cascade="all, delete-orphan", lazy="select")
    users = db.relationship("User", back_populates="department", lazy="select")

    def __repr__(self) -> str:
        return f"<Department {self.code}: {self.name}>"

    def to_dict(self, include_counts: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_counts:
            data["labs_count"] = len(self.labs)
            data["users_count"] = len(self.users)
        return data

