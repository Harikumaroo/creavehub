"""
core/mixins.py

Provides a consistent API response envelope across all CraveHub views.

Success:  { "success": true,  "message": "...", "data": {...} }
Error:    { "success": false, "message": "..." }
"""
from rest_framework import status
from rest_framework.response import Response


class SuccessResponseMixin:
    """
    Mixin for DRF views that enforces the CraveHub response envelope.
    Mix into APIView or generic view subclasses.
    """

    def success_response(
        self,
        data=None,
        message="Success",
        status_code=status.HTTP_200_OK,
    ) -> Response:
        payload = {
            "success": True,
            "message": message,
        }
        if data is not None:
            payload["data"] = data
        return Response(payload, status=status_code)

    def error_response(
        self,
        message="Something went wrong",
        status_code=status.HTTP_400_BAD_REQUEST,
        errors=None,
    ) -> Response:
        payload = {
            "success": False,
            "message": message,
        }
        if errors:
            payload["errors"] = errors
        return Response(payload, status=status_code)
