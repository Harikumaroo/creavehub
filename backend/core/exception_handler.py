"""
CraveHub Global DRF Exception Handler
Register in settings.py under REST_FRAMEWORK → EXCEPTION_HANDLER
"""

import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from core.exceptions import CraveHubBaseException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: dict):
    response = drf_exception_handler(exc, context)

    if isinstance(exc, CraveHubBaseException):
        logger.warning("CraveHub error [%s]: %s", exc.error_code, exc.message)
        return Response(exc.to_dict(), status=exc.status_code)

    if response is not None:
        original_data = response.data
        if isinstance(original_data, list):
            detail = original_data[0] if original_data else "Error"
            errors = {"detail": original_data}
        elif isinstance(original_data, dict):
            detail = original_data.pop("detail", "An error occurred.")
            errors = original_data if original_data else None
        else:
            detail = str(original_data)
            errors = None

        response.data = {
            "success": False,
            "message": str(detail),
            "data": None,
            **({"errors": errors} if errors else {}),
        }
        return response

    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return Response(
        {
            "success": False,
            "message": "An unexpected internal error occurred.",
            "data": None,
            "error_code": "INTERNAL_ERROR",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )