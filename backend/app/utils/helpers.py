"""
app/utils/helpers.py
─────────────────────
Shared utility functions used across the LabLoop Flask application.

Includes
--------
  • success_response / error_response  — standardised JSON envelope helpers
  • paginate_query                     — SQLAlchemy query pagination helper
"""

from __future__ import annotations

from typing import Any

from flask import jsonify


# ── JSON response helpers ─────────────────────────────────────────────────────


def success_response(
    data: Any = None,
    message: str = "",
    status: int = 200,
):
    """
    Build a standardised success JSON response.

    Parameters
    ----------
    data : Any, optional
        The payload to return (dict, list, primitive, or None).
    message : str, optional
        Human-readable description of the outcome.
    status : int, optional
        HTTP status code (default 200).

    Returns
    -------
    tuple[Response, int]
        A Flask `jsonify` response and the HTTP status code.

    Example response body
    ---------------------
    ::

        {
            "success": true,
            "message": "User created successfully.",
            "data": { ... }
        }
    """
    payload: dict = {"success": True, "message": message, "data": data}
    return jsonify(payload), status


def error_response(
    message: str,
    status: int = 400,
    errors: Any = None,
):
    """
    Build a standardised error JSON response.

    Parameters
    ----------
    message : str
        Human-readable error description.
    status : int, optional
        HTTP status code (default 400).
    errors : Any, optional
        Detailed validation errors or additional context (dict or list).

    Returns
    -------
    tuple[Response, int]
        A Flask `jsonify` response and the HTTP status code.

    Example response body
    ---------------------
    ::

        {
            "success": false,
            "message": "Validation failed.",
            "errors": { "email": ["Not a valid email address."] }
        }
    """
    payload: dict = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status


# ── Pagination helper ─────────────────────────────────────────────────────────


def paginate_query(query, page: int = 1, per_page: int = 20) -> dict:
    """
    Paginate a SQLAlchemy *query* object and return a metadata dict.

    Parameters
    ----------
    query : sqlalchemy.orm.Query
        The base query to paginate (filters already applied).
    page : int, optional
        Current page number, 1-indexed (default 1).
    per_page : int, optional
        Number of records per page (default 20, capped at 100).

    Returns
    -------
    dict
        ::

            {
                "items":    [...],   # serialised list of model objects
                "total":    int,     # total matching records
                "pages":    int,     # total number of pages
                "page":     int,     # current page
                "per_page": int      # records per page
            }

    Notes
    -----
    The caller is responsible for serialising `items` (e.g. calling
    `to_dict()` on each element).  This function returns raw ORM objects.
    """
    # Guard against unreasonable values
    page = max(1, int(page))
    per_page = min(max(1, int(per_page)), 100)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "items": pagination.items,
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page,
    }
