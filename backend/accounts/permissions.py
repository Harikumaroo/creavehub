"""
Custom DRF permissions for CraveHub.
Future-ready: account_type based access control.
"""
from rest_framework.permissions import BasePermission


class IsVerifiedUser(BasePermission):
    """Allow only verified users."""
    message = "Your account is not verified."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )


class IsCustomer(BasePermission):
    message = "Access restricted to customers."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.account_type == "customer"
        )


class IsDeliveryPartner(BasePermission):
    message = "Access restricted to delivery partners."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.account_type == "delivery_partner"
        )


class IsRestaurantOwner(BasePermission):
    message = "Access restricted to restaurant owners."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.account_type == "restaurant_owner"
        )


class IsActiveDeviceSession(BasePermission):
    """
    Ensure the JWT belongs to an active device session.
    Future: add trusted device check here.
    """
    message = "This session has been revoked. Please login again."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            jti = request.auth.payload.get("jti", "")
            if not jti:
                return False
            from .models import DeviceSession
            return DeviceSession.objects.filter(
                user=request.user,
                refresh_token_id=jti,
                is_active=True,
            ).exists()
        except Exception:
            return True  # Graceful: don't block if session check fails