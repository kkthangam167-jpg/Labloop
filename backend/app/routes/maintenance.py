"""
app/routes/maintenance.py
──────────────────────────
Maintenance Log blueprint for LabLoop.

All routes prefixed /api/maintenance (registered in app/__init__.py).

Endpoints
---------
  GET    /             – List maintenance logs (role-scoped)
  POST   /             – Create a maintenance task
  GET    /<id>         – Get maintenance task detail
  PATCH  /<id>/status  – Update status (scheduled, in_progress, completed, cancelled)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.maintenance import (
    MaintenanceLog,
    STATUS_SCHEDULED,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
    MAINTENANCE_STATUSES,
    MAINTENANCE_TYPES,
)
from app.models.equipment import Equipment
from app.models.user import ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE
from app.middleware.role_required import role_required, get_current_user
from app.utils.helpers import error_response, success_response, paginate_query

logger = logging.getLogger(__name__)

maintenance_bp = Blueprint("maintenance", __name__)


# ── GET /api/maintenance ──────────────────────────────────────────────────────

@maintenance_bp.route("", methods=["GET"])
@jwt_required()
def list_maintenance():
    """List maintenance logs with optional filters."""
    current_user = get_current_user()
    if not current_user:
        return error_response("User not found.", 404)

    status = request.args.get("status")
    equipment_id = request.args.get("equipment_id", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = MaintenanceLog.query

    if current_user.role == ROLE_LAB_INCHARGE:
        assigned_lab_ids = [
            a.lab_id for a in current_user.lab_assignments if a.revoked_at is None
        ]
        if assigned_lab_ids:
            query = query.join(Equipment).filter(
                Equipment.lab_id.in_(assigned_lab_ids)
            )
        else:
            query = query.filter(MaintenanceLog.id == -1)

    if status:
        query = query.filter(MaintenanceLog.status == status)
    if equipment_id:
        query = query.filter(MaintenanceLog.equipment_id == equipment_id)

    query = query.order_by(MaintenanceLog.scheduled_date.asc())
    paginated = paginate_query(query, page=page, per_page=per_page)
    paginated["items"] = [m.to_dict() for m in paginated["items"]]

    return success_response(paginated, "Maintenance logs retrieved.")


# ── POST /api/maintenance ─────────────────────────────────────────────────────

@maintenance_bp.route("", methods=["POST"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def create_maintenance():
    """Create a new maintenance task."""
    current_user = get_current_user()
    data = request.get_json(silent=True) or {}

    equipment_id = data.get("equipment_id")
    title = (data.get("title") or "").strip()
    m_type = data.get("maintenance_type", "preventive")
    scheduled_date_str = data.get("scheduled_date")

    if not equipment_id or not title:
        return error_response("equipment_id and title are required.", 400)

    equipment = Equipment.query.filter_by(id=equipment_id, is_deleted=False).first()
    if not equipment:
        return error_response("Equipment not found.", 404)

    try:
        s_date = None
        if scheduled_date_str:
            s_date = datetime.strptime(scheduled_date_str, "%Y-%m-%d").date()

        log = MaintenanceLog(
            equipment_id=equipment_id,
            performed_by=current_user.id,
            title=title,
            description=data.get("description", ""),
            maintenance_type=m_type,
            status=STATUS_SCHEDULED,
            scheduled_date=s_date,
            technician_name=data.get("technician_name"),
            technician_contact=data.get("technician_contact"),
        )
        db.session.add(log)
        db.session.commit()
        return success_response(log.to_dict(), "Maintenance task scheduled.", 201)
    except Exception as exc:
        db.session.rollback()
        return error_response(f"Failed to create maintenance task: {str(exc)}", 500)


# ── PATCH /api/maintenance/<id>/status ────────────────────────────────────────

@maintenance_bp.route("/<int:task_id>/status", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def update_maintenance_status(task_id: int):
    """Update maintenance task status."""
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in MAINTENANCE_STATUSES:
        return error_response(
            f"Invalid status. Must be one of: {', '.join(MAINTENANCE_STATUSES)}", 400
        )

    log = MaintenanceLog.query.get(task_id)
    if not log:
        return error_response("Maintenance task not found.", 404)

    log.status = new_status
    if new_status == STATUS_COMPLETED:
        log.completed_date = datetime.now(timezone.utc).date()
        log.resolution_notes = data.get("notes", "Maintenance completed.")
        # Restore equipment status
        if log.equipment:
            from app.models.equipment import STATUS_AVAILABLE
            log.equipment.status = STATUS_AVAILABLE

    db.session.commit()
    return success_response(log.to_dict(), f"Maintenance status updated to '{new_status}'.")

