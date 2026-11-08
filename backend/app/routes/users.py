"""
app/routes/users.py
───────────────────
Users management blueprint for LabLoop (Super Admin only).
"""

from __future__ import annotations
import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.extensions import db
from app.models.user import User, ROLE_SUPER_ADMIN, ROLE_STUDENT, ROLE_LAB_INCHARGE
from app.models.department import Department
from app.models.lab import Lab
from app.middleware.role_required import role_required, get_current_user
from app.schemas.user_schema import AdminCreateUserSchema, AdminUpdateUserSchema
from app.utils.helpers import error_response, success_response, paginate_query

logger = logging.getLogger(__name__)

users_bp = Blueprint("users", __name__)

_create_user_schema = AdminCreateUserSchema()
_update_user_schema = AdminUpdateUserSchema()


@users_bp.route("/stats/summary", methods=["GET"])
@jwt_required()
def get_dashboard_summary():
    """Retrieve statistical summary for dashboards based on requesting user role."""
    current_user = get_current_user()
    if not current_user:
        return error_response("User not found.", 404)

    role = current_user.role

    if role == ROLE_SUPER_ADMIN:
        total_users = User.query.count()
        total_students = User.query.filter_by(role=ROLE_STUDENT).count()
        total_incharges = User.query.filter_by(role=ROLE_LAB_INCHARGE).count()
        total_depts = Department.query.count()
        total_labs = Lab.query.count()

        return success_response({
            "role": role,
            "total_users": total_users,
            "total_students": total_students,
            "total_incharges": total_incharges,
            "total_departments": total_depts,
            "total_labs": total_labs,
            "system_status": "Healthy",
            "security_mode": "Strict Admin-Only Registration",
        }, "Admin summary retrieved.")

    elif role == ROLE_LAB_INCHARGE:
        active_assignments = [a for a in current_user.lab_assignments if a.revoked_at is None]
        assigned_lab_ids = [a.lab_id for a in active_assignments]
        assigned_labs = Lab.query.filter(Lab.id.in_(assigned_lab_ids)).all() if assigned_lab_ids else []

        return success_response({
            "role": role,
            "assigned_labs_count": len(assigned_labs),
            "assigned_labs": [l.to_dict(include_department=True, include_incharges=False) for l in assigned_labs],
            "pending_approvals_count": 0,
            "active_checkins_count": 0,
            "maintenance_tasks_count": 0,
            "open_damage_reports_count": 0,
        }, "Lab In-charge summary retrieved.")

    else:
        dept = current_user.department
        return success_response({
            "role": role,
            "active_bookings_count": 0,
            "completed_sessions_count": 0,
            "damage_reports_count": 0,
            "department": dept.name if dept else "General Sciences",
            "roll_number": current_user.roll_number,
        }, "Student summary retrieved.")


@users_bp.route("", methods=["GET"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def list_users():
    """List users with filtering by role, department, status, or search."""
    role = request.args.get("role")
    dept_id = request.args.get("department_id", type=int)
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = User.query
    if role:
        query = query.filter_by(role=role)
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if search:
        query = query.filter(
            db.or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.roll_number.ilike(f"%{search}%"),
            )
        )

    query = query.order_by(User.id.desc())
    paginated = paginate_query(query, page=page, per_page=per_page)
    items = []
    for u in paginated["items"]:
        d = u.to_dict()
        if u.department:
            d["department"] = {"id": u.department.id, "name": u.department.name, "code": u.department.code}
        items.append(d)
    paginated["items"] = items

    return success_response(paginated, "Users retrieved.")


@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def get_user(user_id: int):
    """Retrieve details for a single user."""
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)
    data = user.to_dict()
    if user.department:
        data["department"] = {"id": user.department.id, "name": user.department.name, "code": user.department.code}
    return success_response(data, "User retrieved.")


@users_bp.route("", methods=["POST"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def create_user():
    """Create a new user account (Super Admin only)."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return error_response("Request body must be valid JSON.", 400)

    try:
        data = _create_user_schema.load(json_data)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)

    if User.query.filter_by(email=data["email"]).first():
        return error_response("A user with this email already exists.", 409)

    if data.get("roll_number"):
        if User.query.filter_by(roll_number=data["roll_number"]).first():
            return error_response("A user with this roll number already exists.", 409)

    try:
        user = User(
            full_name=data["full_name"],
            email=data["email"],
            role=data["role"],
            roll_number=data.get("roll_number"),
            admission_year=data.get("admission_year"),
            department_code=data.get("department_code"),
            phone=data.get("phone"),
            department_id=data.get("department_id"),
            is_active=data.get("is_active", True),
            email_verified=True,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error creating user: %s", exc)
        return error_response("Failed to create user account.", 500)

    return success_response(user.to_dict(), "User account created successfully.", 201)


@users_bp.route("/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def update_user(user_id: int):
    """Update user information (Super Admin only)."""
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)

    json_data = request.get_json(silent=True)
    if not json_data:
        return error_response("Request body must be valid JSON.", 400)

    try:
        data = _update_user_schema.load(json_data)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)

    if "email" in data and data["email"] != user.email:
        if User.query.filter_by(email=data["email"]).first():
            return error_response("Email is already taken.", 409)
        user.email = data["email"]

    if "roll_number" in data and data["roll_number"] != user.roll_number:
        if data["roll_number"] and User.query.filter_by(roll_number=data["roll_number"]).first():
            return error_response("Roll number is already taken.", 409)
        user.roll_number = data["roll_number"]

    for field in ["full_name", "role", "phone", "department_id", "is_active"]:
        if field in data:
            setattr(user, field, data[field])

    if data.get("password"):
        user.set_password(data["password"])

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error updating user: %s", exc)
        return error_response("Failed to update user.", 500)

    return success_response(user.to_dict(), "User updated successfully.")


@users_bp.route("/<int:user_id>/toggle-active", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def toggle_user_active(user_id: int):
    """Toggle user active status."""
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)

    current_user = get_current_user()
    if current_user.id == user.id:
        return error_response("You cannot deactivate your own account.", 400)

    user.is_active = not user.is_active
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error toggling active status: %s", exc)
        return error_response("Failed to update status.", 500)

    status_str = "activated" if user.is_active else "deactivated"
    return success_response(user.to_dict(), f"User {status_str} successfully.")


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN)
def delete_user(user_id: int):
    """Delete a user account."""
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found.", 404)

    current_user = get_current_user()
    if current_user.id == user.id:
        return error_response("You cannot delete your own account.", 400)

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error deleting user: %s", exc)
        return error_response("Failed to delete user.", 500)

    return success_response(None, "User deleted successfully.")

