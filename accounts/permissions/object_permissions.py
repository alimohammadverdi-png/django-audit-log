from rest_framework.permissions import BasePermission
from accounts.models import User


class IsOwnerOrAdmin(BasePermission):
    """
    Allow access if:
    - user is ADMIN
    - or user is the owner of the object
    """

    def has_object_permission(self, request, view, obj):
        user: User = request.user

        # Safety check
        if not user or not user.is_authenticated:
            return False

        # ADMIN has full access
        if user.role == User.Role.ADMIN:
            return True

        # Object owner check
        return hasattr(obj, "owner") and obj.owner == user
