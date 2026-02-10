from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from audit_log.models import AuditLog
from audit_log.context import (
    get_current_user,
    is_audit_logging_disabled,
)


@receiver(post_save)
def audit_log_post_save(sender, instance, created, **kwargs):
    # ⛔ Django not fully ready (early startup)
    if not apps.ready:
        return

    # ⛔ NEVER log audit log itself
    if sender is AuditLog:
        return

    # ⛔ NEVER log migrations (THIS WAS THE MISSING PIECE)
    if sender.__module__.startswith("django.db.migrations"):
        return

    # ⛔ skip raw saves (fixtures, migrations safety net)
    if kwargs.get("raw", False):
        return

    # ⛔ skip when disabled (tests / bulk ops)
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
        # Audit logging must NEVER break migrations / requests / tests
        return
