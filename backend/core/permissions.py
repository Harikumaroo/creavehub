"""
core/permissions.py

Shared DRF permission classes for CraveHub.
"""
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Object-level permission: only the owner of the resource can access it.
    The view/model must expose a `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
