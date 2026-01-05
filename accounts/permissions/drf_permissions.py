# accounts/permissions/drf_permissions.py

from rest_framework.permissions import BasePermission
from accounts.permissions.role_permissions import has_role_permission


class HasRolePermission(BasePermission):
    """
    DRF permission class for role-based access control
    """

    required_permission = None

    def has_permission(self, request, view):
        if not self.required_permission:
            raise ValueError(
                'required_permission is not set on the view'
            )

        return has_role_permission(
            request.user,
            self.required_permission
        )
