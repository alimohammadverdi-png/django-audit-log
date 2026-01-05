# accounts/permissions/role_permissions.py

from accounts.models import User

ROLE_PERMISSION_MAP = {
    User.Role.USER: set(),
    User.Role.STAFF: {
        'products.add_product',
        'products.change_product',
        'products.view_product',
    },
    User.Role.ADMIN: {
        '*',  # دسترسی کامل
    },
}

def has_role_permission(user, permission_codename: str) -> bool:
    """
    Check if user has a permission based on role
    """
    if not user or not user.is_authenticated:
        return False

    allowed_permissions = ROLE_PERMISSION_MAP.get(user.role, set())

    if '*' in allowed_permissions:
        return True

    return permission_codename in allowed_permissions
