from django.db import models


class Action(models.TextChoices):
    CREATE = "CREATE", "Create"
    UPDATE = "UPDATE", "Update"
    DELETE = "DELETE", "Delete"

    LOGIN = "LOGIN", "Login"
    LOGOUT = "LOGOUT", "Logout"

    ACCESS = "ACCESS", "Access"
    PERMISSION_CHANGE = "PERMISSION_CHANGE", "Permission Change"
