"""
app/routes/equipment.py
───────────────────────
Equipment and Category management blueprint for LabLoop.
"""

from __future__ import annotations

import logging
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.extensions import db
from app.models.equipment import (
    Equipment,
    EquipmentCategory,
    STATUS_AVAILABLE,
    EQUIPMENT_STATUSES,
)
from app.models.user import ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE
from app.middleware.role_required import role_required, get_current_user
from app.utils.helpers import error_response, success_response, paginate_query

logger = logging.getLogger(__name__)

equipment_bp = Blueprint("equipment", __name__)


# ── GET /api/equipment/categories ─────────────────────────────────────────────

@equipment_bp.route("/categories", methods=["GET"])
def list_categories():
    """List all active equipment categories."""
    categories = EquipmentCategory.query.filter_by(is_active=True).order_by(EquipmentCategory.name.asc()).all()
    return success_response([c.to_dict(include_count=True) for c in categories], "Categories retrieved.")


# ── GET /api/equipment ────────────────────────────────────────────────────────

@equipment_bp.route("", methods=["GET"])
def list_equipment():
    """
    List equipment with optional filters:
      - lab_id: int
      - category_id: int
      - status: str (available, under_maintenance, etc.)
      - search: str (matches name, model, serial, or manufacturer)
      - page: int (default 1)
      - per_page: int (default 50)
    """
    lab_id = request.args.get("lab_id", type=int)
    category_id = request.args.get("category_id", type=int)
    status = request.args.get("status")
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = Equipment.query.filter_by(is_deleted=False)

    if lab_id:
        query = query.filter_by(lab_id=lab_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            db.or_(
                Equipment.name.ilike(f"%{search}%"),
                Equipment.model_number.ilike(f"%{search}%"),
                Equipment.serial_number.ilike(f"%{search}%"),
                Equipment.manufacturer.ilike(f"%{search}%"),
            )
        )

    query = query.order_by(Equipment.name.asc())
    paginated = paginate_query(query, page=page, per_page=per_page)
    paginated["items"] = [eq.to_dict() for eq in paginated["items"]]

    return success_response(paginated, "Equipment retrieved.")


# ── GET /api/equipment/<id> ───────────────────────────────────────────────────

@equipment_bp.route("/<int:equipment_id>", methods=["GET"])
def get_equipment_detail(equipment_id: int):
    """Retrieve detailed information for a single equipment unit."""
    eq = Equipment.query.filter_by(id=equipment_id, is_deleted=False).first()
    if not eq:
        return error_response("Equipment not found.", 404)
    return success_response(eq.to_dict(), "Equipment details retrieved.")


# ── POST /api/equipment ───────────────────────────────────────────────────────

@equipment_bp.route("", methods=["POST"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def create_equipment():
    """Create a new equipment entry (In-charge or Admin)."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    lab_id = data.get("lab_id")

    if not name or not lab_id:
        return error_response("name and lab_id are required fields.", 400)

    secret_key = current_app.config.get("SECRET_KEY", "dev-secret-key")
    try:
        eq = Equipment(
            name=name,
            lab_id=lab_id,
            category_id=data.get("category_id"),
            model_number=data.get("model_number"),
            serial_number=data.get("serial_number"),
            manufacturer=data.get("manufacturer"),
            quantity_total=data.get("quantity_total", 1),
            quantity_available=data.get("quantity_available", data.get("quantity_total", 1)),
            status=data.get("status", STATUS_AVAILABLE),
            description=data.get("description"),
            location_in_lab=data.get("location_in_lab"),
            purchase_cost=data.get("purchase_cost"),
        )
        eq.generate_qr(secret_key)
        db.session.add(eq)
        db.session.commit()
        logger.info("Equipment created: id=%s name=%s", eq.id, eq.name)
        return success_response(eq.to_dict(), "Equipment created successfully.", 201)
    except Exception as exc:
        db.session.rollback()
        logger.exception("Error creating equipment: %s", exc)
        return error_response(f"Failed to create equipment: {str(exc)}", 500)


# ── PATCH /api/equipment/<id>/status ──────────────────────────────────────────

@equipment_bp.route("/<int:equipment_id>/status", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def update_equipment_status(equipment_id: int):
    """Update operating status of an equipment item."""
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in EQUIPMENT_STATUSES:
        return error_response(f"Invalid status. Allowed values: {EQUIPMENT_STATUSES}", 400)

    eq = Equipment.query.filter_by(id=equipment_id, is_deleted=False).first()
    if not eq:
        return error_response("Equipment not found.", 404)

    eq.status = new_status
    db.session.commit()
    return success_response(eq.to_dict(), f"Equipment status updated to '{new_status}'.")


# ── POST /api/equipment/<id>/generate-qr ──────────────────────────────────────

@equipment_bp.route("/<int:equipment_id>/generate-qr", methods=["POST"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def regenerate_qr(equipment_id: int):
    """Regenerate a cryptographically random HMAC-signed QR token for an equipment unit."""
    eq = Equipment.query.filter_by(id=equipment_id, is_deleted=False).first()
    if not eq:
        return error_response("Equipment not found.", 404)

    secret_key = current_app.config.get("SECRET_KEY", "dev-secret-key")
    token = eq.generate_qr(secret_key)
    db.session.commit()

    return success_response(
        {
            "equipment_id": eq.id,
            "qr_code_token": eq.qr_code_token,
            "qr_code_hmac": eq.qr_code_hmac,
        },
        "QR code token regenerated successfully.",
    )


# ── DELETE /api/equipment/<id> ────────────────────────────────────────────────

@equipment_bp.route("/<int:equipment_id>", methods=["DELETE"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def delete_equipment(equipment_id: int):
    """Soft delete equipment entry."""
    eq = Equipment.query.filter_by(id=equipment_id, is_deleted=False).first()
    if not eq:
        return error_response("Equipment not found.", 404)

    eq.is_deleted = True
    db.session.commit()
    return success_response(None, "Equipment deleted successfully.")

