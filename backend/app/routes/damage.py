"""
app/routes/damage.py
─────────────────────
Damage Report blueprint for LabLoop.

All routes prefixed /api/damage-reports (registered in app/__init__.py).

Endpoints
---------
  GET    /               – List damage reports (role-scoped)
  POST   /               – Submit a new damage report
  GET    /<id>           – Get report detail
  PATCH  /<id>/resolve   – Mark as resolved (admin/incharge)
  PATCH  /<id>/review    – Mark as under-review (admin/incharge)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.damage import (
    DamageReport,
    SEVERITY_MINOR,
    SEVERITY_MODERATE,
    SEVERITY_SEVERE,
    SEVERITY_CRITICAL,
    STATUS_OPEN,
    STATUS_UNDER_REVIEW,
    STATUS_RESOLVED,
    SEVERITY_LEVELS,
)
from app.models.equipment import Equipment
from app.models.user import ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE, ROLE_STUDENT
from app.middleware.role_required import role_required, get_current_user
from app.utils.helpers import error_response, success_response, paginate_query

logger = logging.getLogger(__name__)

damage_bp = Blueprint("damage", __name__)


# ── GET /api/damage-reports ───────────────────────────────────────────────────

@damage_bp.route("", methods=["GET"])
@jwt_required()
def list_damage_reports():
    """
    List damage reports scoped to the requesting user role:
      - Students see their own reports.
      - In-charges see reports for equipment in their assigned labs.
      - Super Admins see all reports.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response("User not found.", 404)

    status = request.args.get("status")
    equipment_id = request.args.get("equipment_id", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = DamageReport.query

    if current_user.role == ROLE_STUDENT:
        query = query.filter_by(reported_by=current_user.id)
    elif current_user.role == ROLE_LAB_INCHARGE:
        assigned_lab_ids = [
            a.lab_id for a in current_user.lab_assignments if a.revoked_at is None
        ]
        if assigned_lab_ids:
            query = query.join(Equipment).filter(
                Equipment.lab_id.in_(assigned_lab_ids)
            )
        else:
            query = query.filter(DamageReport.id == -1)

    if status:
        query = query.filter(DamageReport.status == status)
    if equipment_id:
        query = query.filter(DamageReport.equipment_id == equipment_id)

    query = query.order_by(DamageReport.created_at.desc())
    paginated = paginate_query(query, page=page, per_page=per_page)
    paginated["items"] = [r.to_dict() for r in paginated["items"]]

    return success_response(paginated, "Damage reports retrieved.")


# ── POST /api/damage-reports ──────────────────────────────────────────────────

@damage_bp.route("", methods=["POST"])
@jwt_required()
def create_damage_report():
    """Submit a new damage report for a piece of equipment."""
    current_user = get_current_user()
    if not current_user:
        return error_response("User not found.", 404)

    data = request.get_json(silent=True) or {}
    equipment_id = data.get("equipment_id")
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    severity = data.get("severity", SEVERITY_MODERATE)
    affects_availability = bool(data.get("affects_availability", False))
    booking_id = data.get("booking_id")

    if not equipment_id or not title or not description:
        return error_response(
            "equipment_id, title, and description are required.", 400
        )

    if severity not in SEVERITY_LEVELS:
        return error_response(
            f"severity must be one of: {', '.join(SEVERITY_LEVELS)}", 400
        )

    equipment = Equipment.query.filter_by(id=equipment_id, is_deleted=False).first()
    if not equipment:
        return error_response("Equipment not found.", 404)

    try:
        report = DamageReport(
            equipment_id=equipment_id,
            reported_by=current_user.id,
            booking_id=booking_id,
            title=title,
            description=description,
            severity=severity,
            status=STATUS_OPEN,
            affects_availability=affects_availability,
        )
        db.session.add(report)

        # If the report marks equipment as unavailable, update status
        if affects_availability:
            from app.models.equipment import STATUS_UNDER_MAINTENANCE
            equipment.status = STATUS_UNDER_MAINTENANCE

        db.session.commit()
        logger.info(
            "Damage report created: id=%s equipment=%s by=%s",
            report.id, equipment_id, current_user.email,
        )
        return success_response(report.to_dict(), "Damage report submitted.", 201)
    except Exception as exc:
        db.session.rollback()
        return error_response(f"Failed to submit report: {str(exc)}", 500)


# ── GET /api/damage-reports/<id> ──────────────────────────────────────────────

@damage_bp.route("/<int:report_id>", methods=["GET"])
@jwt_required()
def get_damage_report(report_id: int):
    """Get a specific damage report by ID."""
    current_user = get_current_user()
    if not current_user:
        return error_response("User not found.", 404)

    report = DamageReport.query.get(report_id)
    if not report:
        return error_response("Damage report not found.", 404)

    # Students can only see their own reports
    if current_user.role == ROLE_STUDENT and report.reported_by != current_user.id:
        return error_response("You do not have access to this report.", 403)

    return success_response(report.to_dict(), "Damage report retrieved.")


# ── PATCH /api/damage-reports/<id>/review ─────────────────────────────────────

@damage_bp.route("/<int:report_id>/review", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def mark_under_review(report_id: int):
    """Mark a damage report as under review."""
    report = DamageReport.query.get(report_id)
    if not report:
        return error_response("Damage report not found.", 404)

    report.status = STATUS_UNDER_REVIEW
    db.session.commit()
    return success_response(report.to_dict(), "Report marked as under review.")


# ── PATCH /api/damage-reports/<id>/resolve ────────────────────────────────────

@damage_bp.route("/<int:report_id>/resolve", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def resolve_damage_report(report_id: int):
    """Resolve a damage report and optionally restore equipment availability."""
    current_user = get_current_user()
    data = request.get_json(silent=True) or {}
    report = DamageReport.query.get(report_id)
    if not report:
        return error_response("Damage report not found.", 404)

    report.status = STATUS_RESOLVED
    report.resolution_notes = data.get("resolution_notes", "Resolved by lab in-charge.")
    report.resolved_by = current_user.id
    report.resolved_at = datetime.now(timezone.utc)

    # Optionally restore equipment to available
    if data.get("restore_equipment", False) and report.equipment:
        from app.models.equipment import STATUS_AVAILABLE
        report.equipment.status = STATUS_AVAILABLE

    db.session.commit()
    logger.info("Damage report %s resolved by %s", report_id, current_user.email)
    return success_response(report.to_dict(), "Damage report resolved.")

