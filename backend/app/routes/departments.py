"""
app/routes/departments.py
─────────────────────────
Departments management blueprint for LabLoop.
"""

from __future__ import annotations
import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.extensions import db
from app.models.department import Department
from app.models.user import ROLE_SUPER_ADMIN
from app.middleware.role_required import role_required
from app.schemas.department_schema import DepartmentSchema, UpdateDepartmentSchema
from app.utils.helpers import error_response, success_response, paginate_query

logger = logging.getLogger(__name__)

departments_bp = Blueprint("departments", __name__)

_department_schema = DepartmentSchema()
_update_department_schema = UpdateDepartmentSchema()


@departments_bp.route("", methods=["GET"])
def list_departments():
    """List all departments (public/authenticated)."""
    search = request.args.get("search", "").strip()
    active_only = request.args.get("active_only", "false").lower() == "true"
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = Department.query
    if search:
        query = query.filter(
            db.or_(
                Department.name.ilike(f"%{search}%"),
                Department.code.ilike(f"%{search}%"),
            )
        )
    if active_only:
        query = query.filter_by(is_active=True)

    query = query.order_by(Department.name.asc())
    paginated = paginate_query(query, page=page, per_page=per_page)
    items = [d.to_dict(include_counts=True) for d in paginated["items"]]
    paginated["items"] = items

    return success_response(paginated, "Departments retrieved.")


@departments_bp.route("/<int:dept_id>", methods=["GET"])
def get_department(dept_id: int):
    """Retrieve details for a single department."""
    dept = db.session.get(Department, dept_id)
    if not dept:
        return error_response("Department not found.", 404)
    return success_response(dept.to_dict(include_counts=True), "Department retrieved.")


@departments_bp.route("", methods=["POST"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def create_department():
    """Create a new department (Super Admin only)."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return error_response("Request body must be valid JSON.", 400)

    try:
        data = _department_schema.load(json_data)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)

    if Department.query.filter_by(code=data["code"]).first():
        return error_response("A department with this code already exists.", 409)
    if Department.query.filter_by(name=data["name"]).first():
        return error_response("A department with this name already exists.", 409)

    try:
        dept = Department(
            name=data["name"],
            code=data["code"],
            description=data.get("description"),
            is_active=data.get("is_active", True),
        )
        db.session.add(dept)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error creating department: %s", exc)
        return error_response("Failed to create department.", 500)

    return success_response(dept.to_dict(include_counts=True), "Department created successfully.", 201)


@departments_bp.route("/<int:dept_id>", methods=["PUT", "PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def update_department(dept_id: int):
    """Update department details (Super Admin only)."""
    dept = db.session.get(Department, dept_id)
    if not dept:
        return error_response("Department not found.", 404)

    json_data = request.get_json(silent=True)
    if not json_data:
        return error_response("Request body must be valid JSON.", 400)

    try:
        data = _update_department_schema.load(json_data)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)

    if "code" in data and data["code"] != dept.code:
        if Department.query.filter_by(code=data["code"]).first():
            return error_response("A department with this code already exists.", 409)
        dept.code = data["code"]

    if "name" in data and data["name"] != dept.name:
        if Department.query.filter_by(name=data["name"]).first():
            return error_response("A department with this name already exists.", 409)
        dept.name = data["name"]

    if "description" in data:
        dept.description = data["description"]
    if "is_active" in data:
        dept.is_active = data["is_active"]

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error updating department: %s", exc)
        return error_response("Failed to update department.", 500)

    return success_response(dept.to_dict(include_counts=True), "Department updated successfully.")


@departments_bp.route("/<int:dept_id>", methods=["DELETE"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def delete_department(dept_id: int):
    """Delete a department (Super Admin only)."""
    dept = db.session.get(Department, dept_id)
    if not dept:
        return error_response("Department not found.", 404)

    try:
        db.session.delete(dept)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error deleting department: %s", exc)
        return error_response("Failed to delete department.", 500)

    return success_response(None, "Department deleted successfully.")

