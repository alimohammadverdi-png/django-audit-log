import sys
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from audit_log.models import AuditLog
from audit_log.context import (
    get_current_user,
    is_audit_logging_disabled,
)

# ⛔ HARD STOP — do NOT even register signals during migrate / test
if any(cmd in sys.argv for cmd in ["migrate", "makemigrations", "pytest", "test"]):
    pass
else:

    @receiver(post_save)
    def audit_log_post_save(sender, instance, created, **kwargs):

        if not apps.ready:
            return

        # ⛔ never log audit log itself
        if sender is AuditLog:
            return

        # ⛔ never log django migration models
        if sender.__module__.startswith("django.db.migrations"):
            return

        # ⛔ raw saves (fixtures, migrations)
        if kwargs.get("raw", False):
            return

        if is_audit_logging_disabled():
            return

        try:
            user = get_current_user()

            content_type = ContentType.objects.get_for_model(
                sender,
                for_concrete_model=False,
            )

            AuditLog.objects.create(
                user=user,
                action="create" if created else "update",
                resource=sender.__name__,
                content_type=content_type,
                object_id=str(instance.pk),
                source="signal",
            )

        except Exception:
            # ✅ ABSOLUTELY FAIL‑SAFE
            return
