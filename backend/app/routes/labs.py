"""
app/routes/labs.py
──────────────────
Laboratory and Lab Assignment management blueprint for LabLoop.
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.extensions import db
from app.models.lab import Lab, LabAssignment
from app.models.department import Department
from app.models.user import User, ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE
from app.middleware.role_required import role_required, get_current_user
from app.schemas.lab_schema import LabSchema, UpdateLabSchema, AssignInchargeSchema
from app.utils.helpers import error_response, success_response, paginate_query

logger = logging.getLogger(__name__)

labs_bp = Blueprint("labs", __name__)

_lab_schema = LabSchema()
_update_lab_schema = UpdateLabSchema()
_assign_schema = AssignInchargeSchema()


@labs_bp.route("", methods=["GET"])
def list_labs():
    """List labs with optional filtering by department, search, or active status."""
    department_id = request.args.get("department_id", type=int)
    search = request.args.get("search", "").strip()
    active_only = request.args.get("active_only", "false").lower() == "true"
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = Lab.query
    if department_id:
        query = query.filter_by(department_id=department_id)
    if search:
        query = query.filter(
            db.or_(
                Lab.name.ilike(f"%{search}%"),
                Lab.location.ilike(f"%{search}%"),
            )
        )
    if active_only:
        query = query.filter_by(is_active=True)

    query = query.order_by(Lab.name.asc())
    paginated = paginate_query(query, page=page, per_page=per_page)
    items = [lab.to_dict(include_department=True, include_incharges=True) for lab in paginated["items"]]
    paginated["items"] = items

    return success_response(paginated, "Labs retrieved.")


@labs_bp.route("/<int:lab_id>", methods=["GET"])
def get_lab(lab_id: int):
    """Retrieve details for a single lab."""
    lab = db.session.get(Lab, lab_id)
    if not lab:
        return error_response("Lab not found.", 404)
    return success_response(lab.to_dict(include_department=True, include_incharges=True), "Lab retrieved.")


@labs_bp.route("", methods=["POST"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def create_lab():
    """Create a new laboratory (Super Admin only)."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return error_response("Request body must be valid JSON.", 400)

    try:
        data = _lab_schema.load(json_data)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)

    dept = db.session.get(Department, data["department_id"])
    if not dept:
        return error_response("Referenced department does not exist.", 400)

    try:
        lab = Lab(
            department_id=data["department_id"],
            name=data["name"],
            location=data.get("location"),
            description=data.get("description"),
            capacity=data.get("capacity", 30),
            is_active=data.get("is_active", True),
        )
        db.session.add(lab)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error creating lab: %s", exc)
        return error_response("Failed to create laboratory.", 500)

    return success_response(lab.to_dict(include_department=True, include_incharges=True), "Laboratory created successfully.", 201)


@labs_bp.route("/<int:lab_id>", methods=["PUT", "PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def update_lab(lab_id: int):
    """Update lab information (Super Admin only)."""
    lab = db.session.get(Lab, lab_id)
    if not lab:
        return error_response("Lab not found.", 404)

    json_data = request.get_json(silent=True)
    if not json_data:
        return error_response("Request body must be valid JSON.", 400)

    try:
        data = _update_lab_schema.load(json_data)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)

    if "department_id" in data:
        dept = db.session.get(Department, data["department_id"])
        if not dept:
            return error_response("Referenced department does not exist.", 400)
        lab.department_id = data["department_id"]

    for field in ["name", "location", "description", "capacity", "is_active"]:
        if field in data:
            setattr(lab, field, data[field])

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error updating lab: %s", exc)
        return error_response("Failed to update laboratory.", 500)

    return success_response(lab.to_dict(include_department=True, include_incharges=True), "Laboratory updated successfully.")


@labs_bp.route("/<int:lab_id>", methods=["DELETE"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def delete_lab(lab_id: int):
    """Delete a laboratory (Super Admin only)."""
    lab = db.session.get(Lab, lab_id)
    if not lab:
        return error_response("Lab not found.", 404)

    try:
        db.session.delete(lab)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error deleting lab: %s", exc)
        return error_response("Failed to delete laboratory.", 500)

    return success_response(None, "Laboratory deleted successfully.")


@labs_bp.route("/<int:lab_id>/incharges", methods=["POST"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def assign_incharge(lab_id: int):
    """Assign a Lab In-charge to a laboratory."""
    lab = db.session.get(Lab, lab_id)
    if not lab:
        return error_response("Lab not found.", 404)

    json_data = request.get_json(silent=True)
    if not json_data:
        return error_response("Request body must be valid JSON.", 400)

    try:
        data = _assign_schema.load(json_data)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)

    user = db.session.get(User, data["user_id"])
    if not user:
        return error_response("User not found.", 404)
    if user.role != ROLE_LAB_INCHARGE:
        return error_response("Assigned user must have the lab_incharge role.", 400)

    # Check existing active assignment
    existing = LabAssignment.query.filter_by(lab_id=lab.id, user_id=user.id, revoked_at=None).first()
    if existing:
        return error_response("User is already actively assigned to this laboratory.", 409)

    # If marked primary, unmark other primary assignments in this lab
    is_primary = data.get("is_primary", False)
    if is_primary:
        LabAssignment.query.filter_by(lab_id=lab.id, revoked_at=None).update({"is_primary": False})

    try:
        assignment = LabAssignment(
            lab_id=lab.id,
            user_id=user.id,
            is_primary=is_primary,
        )
        db.session.add(assignment)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error assigning incharge: %s", exc)
        return error_response("Failed to assign in-charge to lab.", 500)

    return success_response(assignment.to_dict(), "Lab In-charge assigned successfully.", 201)


@labs_bp.route("/<int:lab_id>/incharges/<int:user_id>", methods=["DELETE"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def revoke_incharge(lab_id: int, user_id: int):
    """Revoke a Lab In-charge assignment."""
    assignment = LabAssignment.query.filter_by(lab_id=lab_id, user_id=user_id, revoked_at=None).first()
    if not assignment:
        return error_response("Active assignment not found.", 404)

    try:
        assignment.revoked_at = datetime.now(timezone.utc)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error revoking incharge: %s", exc)
        return error_response("Failed to revoke lab assignment.", 500)

    return success_response(None, "Lab assignment revoked successfully.")

