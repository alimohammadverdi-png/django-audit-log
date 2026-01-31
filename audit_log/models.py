# audit_log/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Action(models.TextChoices):
    CREATE = "CREATE", "Create"
    UPDATE = "UPDATE", "Update"
    DELETE = "DELETE", "Delete"
    RESTORE = "RESTORE", "Restore"
    HARD_DELETE = "HARD_DELETE", "Hard Delete"
    USER_LOGIN = "USER_LOGIN", "User Login"


class AuditLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        db_index=True,
    )

    resource = models.CharField(
        max_length=100,
        db_index=True,
        default="",
    )

    status = models.CharField(
        max_length=10,
        default="INFO",
        db_index=True,
    )

    description = models.TextField(blank=True, default="")

    source = models.CharField(
        max_length=10,
        default="api",
        db_index=True,
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )
    content_object = GenericForeignKey("content_type", "object_id")

    changes = models.JSONField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-timestamp",)
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        user_display = self.user.username if self.user else "system"
        if self.content_object is None:
            obj_info = self.resource or "General Event"
            return f"{user_display} | {self.action} | {obj_info}"
        return f"{user_display} | {self.action} | {self.content_object}"
