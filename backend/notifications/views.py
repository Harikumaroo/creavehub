"""
CraveHub — Notifications Views
"""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from core.exceptions import CraveHubBaseException
from core.helpers import error_response, paginated_response, success_response
from core.helpers.pagination import PaginationParams
from core.permissions import IsAuthenticatedAndActive

from .serializers import (
    MarkReadSerializer, NotificationSerializer, PushTokenSerializer,
)
from .services import NotificationService


class NotificationListView(APIView):
    """
    GET /api/v1/notifications/
    Returns paginated notifications for the authenticated user.
    Supports ?unread=true to filter unread only.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request):
        params    = PaginationParams.from_request(request)
        notifs, total = NotificationService.get_user_notifications(
            user=request.user, params=params,
        )
        serializer = NotificationSerializer(notifs, many=True)
        unread_count = NotificationService.get_unread_count(request.user)
        data = paginated_response(
            data=serializer.data,
            page=params.page,
            page_size=params.page_size,
            total_count=total,
            message="Notifications fetched successfully",
        )
        # Inject unread_count into response
        data.data["unread_count"] = unread_count
        return data


class MarkReadView(APIView):
    """
    POST /api/v1/notifications/mark-read/
    Mark specific notifications as read.
    Body: {"notification_ids": ["uuid", ...]}
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        serializer = MarkReadSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation failed", errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        updated = NotificationService.mark_read(
            user=request.user,
            notification_ids=serializer.validated_data["notification_ids"],
        )
        return success_response(
            data={"marked_read": updated},
            message=f"{updated} notification(s) marked as read",
        )


class MarkAllReadView(APIView):
    """
    POST /api/v1/notifications/mark-all-read/
    Marks every unread notification for the user as read.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        updated = NotificationService.mark_all_read(user=request.user)
        return success_response(
            data={"marked_read": updated},
            message="All notifications marked as read",
        )


class PushTokenView(APIView):
    """
    POST /api/v1/notifications/push-token/
    Register or update a push notification token.
    Body: {"token": "...", "platform": "android|ios|web"}
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        serializer = PushTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation failed", errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        token = NotificationService.register_push_token(
            user=request.user,
            token=serializer.validated_data["token"],
            platform=serializer.validated_data["platform"],
        )
        return success_response(
            data=PushTokenSerializer(token).data,
            message="Push token registered successfully",
        )
