"""
CraveHub API Response Helpers
Standard envelope for every API response.
"""

from __future__ import annotations
from typing import Any
from rest_framework import status
from rest_framework.response import Response


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    meta: dict | None = None,
) -> Response:
    payload: dict = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        payload["meta"] = meta
    return Response(payload, status=status_code)


def created_response(
    data: Any = None,
    message: str = "Resource created successfully",
    meta: dict | None = None,
) -> Response:
    return success_response(data, message, status.HTTP_201_CREATED, meta)


def error_response(
    message: str = "An error occurred",
    errors: dict | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_code: str | None = None,
) -> Response:
    payload: dict = {
        "success": False,
        "message": message,
        "data": None,
    }
    if errors:
        payload["errors"] = errors
    if error_code:
        payload["error_code"] = error_code
    return Response(payload, status=status_code)


def not_found_response(message: str = "Resource not found") -> Response:
    return error_response(
        message,
        status_code=status.HTTP_404_NOT_FOUND,
        error_code="NOT_FOUND",
    )


def validation_error_response(
    errors: dict,
    message: str = "Validation failed",
) -> Response:
    return error_response(
        message,
        errors=errors,
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="VALIDATION_ERROR",
    )


def paginated_response(
    data: Any,
    page: int,
    page_size: int,
    total_count: int,
    message: str = "Data fetched successfully",
) -> Response:
    import math
    total_pages = math.ceil(total_count / page_size) if page_size else 1
    meta = {
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }
    }
    return success_response(data, message, meta=meta)