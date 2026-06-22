"""
CraveHub Custom DRF Permissions
"""

from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAuthenticatedAndActive(IsAuthenticated):
    def has_permission(self, request, view) -> bool:
        return (
            super().has_permission(request, view)
            and request.user.is_active
        )


class IsAdminOrReadOnly(BasePermission):
    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

    def has_permission(self, request, view) -> bool:
        if request.method in self.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_staff:
            return True
        return getattr(obj, "user_id", None) == request.user.id


class AllowAny(BasePermission):
    def has_permission(self, request, view) -> bool:
        return True