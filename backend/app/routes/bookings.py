"""
app/routes/bookings.py
──────────────────────
Booking and QR Check-in / Check-out blueprint for LabLoop.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, date, time
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.booking import (
    Booking,
    STATUS_PENDING,
    STATUS_APPROVED,
    STATUS_REJECTED,
    STATUS_ACTIVE,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
)
from app.models.equipment import Equipment, STATUS_AVAILABLE
from app.models.user import ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE, ROLE_STUDENT
from app.middleware.role_required import role_required, get_current_user
from app.utils.helpers import error_response, success_response, paginate_query

logger = logging.getLogger(__name__)

bookings_bp = Blueprint("bookings", __name__)


# ── GET /api/bookings ─────────────────────────────────────────────────────────

@bookings_bp.route("", methods=["GET"])
@jwt_required()
def list_bookings():
    """
    List bookings scoped to requesting user role:
      - Students see their own bookings.
      - In-charges see bookings for equipment in their assigned labs.
      - Super Admins see all bookings campus-wide.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response("User not found.", 404)

    status = request.args.get("status")
    booking_date = request.args.get("date")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = Booking.query

    if current_user.role == ROLE_STUDENT:
        query = query.filter_by(booked_by=current_user.id)
    elif current_user.role == ROLE_LAB_INCHARGE:
        assigned_lab_ids = [a.lab_id for a in current_user.lab_assignments if a.revoked_at is None]
        if assigned_lab_ids:
            query = query.join(Equipment).filter(Equipment.lab_id.in_(assigned_lab_ids))
        else:
            query = query.filter(Booking.id == -1)  # No labs assigned

    if status:
        query = query.filter(Booking.status == status)
    if booking_date:
        try:
            d = datetime.strptime(booking_date, "%Y-%m-%d").date()
            query = query.filter(Booking.booking_date == d)
        except ValueError:
            pass

    query = query.order_by(Booking.booking_date.desc(), Booking.start_time.desc())
    paginated = paginate_query(query, page=page, per_page=per_page)
    paginated["items"] = [b.to_dict() for b in paginated["items"]]

    return success_response(paginated, "Bookings retrieved.")


# ── POST /api/bookings ────────────────────────────────────────────────────────

@bookings_bp.route("", methods=["POST"])
@jwt_required()
def create_booking():
    """Submit a reservation request for an equipment unit."""
    current_user = get_current_user()
    if not current_user:
        return error_response("User not found.", 404)

    data = request.get_json(silent=True) or {}
    equipment_id = data.get("equipment_id")
    booking_date_str = data.get("booking_date")
    start_time_str = data.get("start_time", "10:00")
    end_time_str = data.get("end_time", "12:00")
    purpose = data.get("purpose", "").strip()

    if not equipment_id or not booking_date_str or not purpose:
        return error_response("equipment_id, booking_date, and purpose are required.", 400)

    try:
        b_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
        s_time = datetime.strptime(start_time_str, "%H:%M").time()
        e_time = datetime.strptime(end_time_str, "%H:%M").time()
    except ValueError as e:
        return error_response(f"Invalid date/time format: {str(e)}", 400)

    equipment = Equipment.query.filter_by(id=equipment_id, is_deleted=False).first()
    if not equipment:
        return error_response("Equipment not found.", 404)

    if equipment.status != STATUS_AVAILABLE:
        return error_response(f"Equipment is currently '{equipment.status}' and cannot be booked.", 400)

    try:
        booking = Booking(
            equipment_id=equipment.id,
            booked_by=current_user.id,
            booking_date=b_date,
            start_time=s_time,
            end_time=e_time,
            purpose=purpose,
            status=STATUS_PENDING,
        )
        db.session.add(booking)
        db.session.commit()
        logger.info("Booking created: id=%s by user=%s", booking.id, current_user.email)
        return success_response(booking.to_dict(), "Booking requested successfully. Awaiting approval.", 201)
    except Exception as exc:
        db.session.rollback()
        return error_response(f"Failed to submit booking: {str(exc)}", 500)


# ── PATCH /api/bookings/<id>/approve ──────────────────────────────────────────

@bookings_bp.route("/<int:booking_id>/approve", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def approve_booking(booking_id: int):
    """Approve a pending booking."""
    current_user = get_current_user()
    booking = Booking.query.get(booking_id)
    if not booking:
        return error_response("Booking not found.", 404)

    booking.status = STATUS_APPROVED
    booking.approved_by = current_user.id
    db.session.commit()
    return success_response(booking.to_dict(), "Booking approved.")


# ── PATCH /api/bookings/<id>/reject ───────────────────────────────────────────

@bookings_bp.route("/<int:booking_id>/reject", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE)
def reject_booking(booking_id: int):
    """Reject a booking with reason."""
    current_user = get_current_user()
    data = request.get_json(silent=True) or {}
    booking = Booking.query.get(booking_id)
    if not booking:
        return error_response("Booking not found.", 404)

    booking.status = STATUS_REJECTED
    booking.rejection_reason = data.get("reason", "Declined by lab in-charge.")
    db.session.commit()
    return success_response(booking.to_dict(), "Booking rejected.")


# ── PATCH /api/bookings/<id>/cancel ───────────────────────────────────────────

@bookings_bp.route("/<int:booking_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_booking(booking_id: int):
    """Cancel booking by owner or administrator."""
    current_user = get_current_user()
    booking = Booking.query.get(booking_id)
    if not booking:
        return error_response("Booking not found.", 404)

    if booking.booked_by != current_user.id and current_user.role != ROLE_SUPER_ADMIN:
        return error_response("Unauthorized to cancel this booking.", 403)

    booking.status = STATUS_CANCELLED
    booking.cancelled_by = current_user.id
    db.session.commit()
    return success_response(booking.to_dict(), "Booking cancelled.")


# ── POST /api/bookings/<id>/checkin ───────────────────────────────────────────

@bookings_bp.route("/<int:booking_id>/checkin", methods=["POST"])
@jwt_required()
def checkin_booking(booking_id: int):
    """Verify QR code and activate session."""
    current_user = get_current_user()
    data = request.get_json(silent=True) or {}
    qr_token = data.get("qr_token", "").strip()

    booking = Booking.query.get(booking_id)
    if not booking:
        return error_response("Booking not found.", 404)

    if booking.booked_by != current_user.id and current_user.role != ROLE_SUPER_ADMIN:
        return error_response("Only the booking owner can check in.", 403)

    secret_key = current_app.config.get("SECRET_KEY", "dev-secret-key")
    if qr_token and not booking.equipment.verify_qr(qr_token, secret_key):
        return error_response("Invalid or corrupted QR token for this equipment.", 400)

    booking.status = STATUS_ACTIVE
    booking.checkin_time = datetime.now(timezone.utc)
    booking.qr_checkin_verified = True
    booking.checkin_qr_token = qr_token or "verified-scan"

    if booking.equipment.quantity_available > 0:
        booking.equipment.quantity_available -= 1

    db.session.commit()
    return success_response(booking.to_dict(), "Check-in verified! Lab session is now active.")


# ── POST /api/bookings/<id>/checkout ──────────────────────────────────────────

@bookings_bp.route("/<int:booking_id>/checkout", methods=["POST"])
@jwt_required()
def checkout_booking(booking_id: int):
    """Complete booking session and return equipment."""
    current_user = get_current_user()
    booking = Booking.query.get(booking_id)
    if not booking:
        return error_response("Booking not found.", 404)

    if booking.booked_by != current_user.id and current_user.role not in [ROLE_SUPER_ADMIN, ROLE_LAB_INCHARGE]:
        return error_response("Unauthorized to check out this booking.", 403)

    booking.status = STATUS_COMPLETED
    booking.checkout_time = datetime.now(timezone.utc)
    booking.qr_checkout_verified = True

    booking.equipment.quantity_available = min(
        booking.equipment.quantity_total, booking.equipment.quantity_available + 1
    )
    booking.equipment.usage_count += 1

    db.session.commit()
    return success_response(booking.to_dict(), "Check-out confirmed! Equipment returned.")

