# audit_log/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class AuditLog(models.Model):
    """
    Generic audit log for tracking model changes
    """

    # -----------------------------
    # Core metadata
    # -----------------------------
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        help_text="User who performed the action",
    )

    action = models.CharField(
        max_length=50,
        db_index=True,
        help_text="create | update | delete | restore | hard_delete | USER_LOGIN | ...",
    )
    
    # ------------------ NEW FIELDS START ------------------
    resource = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Name of the resource (e.g., 'Product', 'Order', 'User')",
        default=""
    )

    status = models.CharField(
        max_length=10,
        db_index=True,
        help_text="SUCCESS | FAILED | INFO",
        default="INFO"
    )

    description = models.TextField(
        blank=True,
        help_text="A human-readable summary of the action.",
        default=""
    )
    # ------------------ NEW FIELDS END --------------------

    source = models.CharField(
        max_length=10,
        db_index=True,
        default="api",
        help_text="admin | api | shell",
    )

    # -----------------------------
    # Target object (Generic FK)
    # -----------------------------
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True, # این فیلد می‌تواند نال باشد برای لاگ‌هایی مثل USER_LOGIN که به شیء خاصی مرتبط نیستند
        blank=True,
    )
    object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    # -----------------------------
    # Change details
    # -----------------------------
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text="Changed fields: old vs new values",
    )

    # -----------------------------
    # Timestamp
    # -----------------------------
    # تغییر created_at به timestamp و حذف auto_now_add برای کنترل دستی در تست‌ها
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action occurred (renamed from created_at)"
    )

    class Meta:
        # تغییر ordering برای استفاده از timestamp
        ordering = ("-timestamp",)
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        user_display = self.user.username if self.user else "system"
        # استفاده از description برای لاگ‌های بدون شیء هدف
        if self.content_object is None:
            obj_info = f"(deleted object #{self.object_id})" if self.object_id else self.resource or "General Event"
            return (
                f"{user_display} | {self.action} "
                f"{obj_info} "
                f"[{self.source}] - {self.description[:30]}..."
            )

        return (
            f"{user_display} | {self.action} "
            f"{self.content_object} "
            f"[{self.source}]"
        )
