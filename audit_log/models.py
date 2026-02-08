from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        BULK_DELETE = "bulk_delete", "Bulk delete"
        BULK_UPDATE = "bulk_update", "Bulk update"
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )

    action = models.CharField(max_length=50, db_index=True)
    resource = models.CharField(
        max_length=255, default="", db_index=True
    )

    status = models.CharField(
        max_length=10, default="INFO", db_index=True
    )
    description = models.TextField(blank=True, default="")

    source = models.CharField(
        max_length=10, default="api", db_index=True
    )

    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    object_id = models.CharField(
        max_length=64, null=True, blank=True
    )

    changes = models.JSONField(null=True, blank=True)

    timestamp = models.DateTimeField(
        auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["resource"]),
            models.Index(fields=["status"]),
            models.Index(fields=["source"]),
            models.Index(fields=["user"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    @property
    def object_type(self):
        return (
            self.content_type.model_class().__name__
            if self.content_type else None
        )

    def __str__(self):
        return f"{self.user or 'system'} | {self.action} | {self.resource}"
