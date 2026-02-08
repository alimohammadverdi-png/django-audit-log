from django.db import models


class Action(models.TextChoices):
    CREATE = "CREATE", "Create"
    UPDATE = "UPDATE", "Update"
    DELETE = "DELETE", "Delete"

    LOGIN = "LOGIN", "Login"
    LOGOUT = "LOGOUT", "Logout"

    ACCESS = "ACCESS", "Access"
    PERMISSION_CHANGE = "PERMISSION_CHANGE", "Permission Change"
# audit_log/constants.py

IGNORED_FIELDS = {
    "updated_at",
    "modified",
    "last_login",
}

# Number of days to keep audit logs before cleanup
AUDIT_LOG_RETENTION_DAYS = 180