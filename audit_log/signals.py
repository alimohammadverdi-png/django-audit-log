from django.apps import apps
from django.db import connection
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from audit_log.models import AuditLog
from audit_log.utils import compute_changes
from audit_log.context import get_current_user, is_audit_logging_disabled

print("✅ LOADED audit_log.signals — FINAL MIGRATION SAFE VERSION")

# -------------------------------------------------
# ✅ HARD GUARDS (NO DB TOUCH BEFORE SAFE)
# -------------------------------------------------

def _auditlog_table_exists() -> bool:
    try:
        return AuditLog._meta.db_table in connection.introspection.table_names()
    except Exception:
        return False


def _is_migration_model(sender) -> bool:
    return (
        sender.__module__.startswith("django.db.migrations")
        or sender.__name__ == "Migration"
        or sender._meta.app_label == "migrations"
    )


def _should_skip(sender, **kwargs) -> bool:
    # ✅ apps not ready (startup / migrate)
    if not apps.ready:
        return True

    # ✅ raw saves (fixtures)
    if kwargs.get("raw"):
        return True

    # ✅ unmanaged models
    if not sender._meta.managed:
        return True

    # ✅ migration models (CRITICAL)
    if _is_migration_model(sender):
        return True

    # ✅ audit logging disabled
    if is_audit_logging_disabled():
        return True

    # ✅ audit_log table not ready
    if not _auditlog_table_exists():
        return True

    # ✅ prevent recursion
    if sender in {AuditLog, ContentType}:
        return True

    return False


# -------------------------------------------------
# ✅ post_save with Metrics (SAFE)
# -------------------------------------------------

@receiver(post_save)
def audit_log_post_save(sender, instance, created, **kwargs):
    if _should_skip(sender, **kwargs):
        return

    try:
        # ✅ ONLY NOW it is safe to touch DB
        user = get_current_user()
        content_type = ContentType.objects.get_for_model(sender)

        changes = None
        if not created and hasattr(instance, "_auditlog_before"):
            changes = compute_changes(
                instance._auditlog_before,
                instance.__dict__,
            )

        if not created and not changes:
            return

        try:
            from audit_log.metrics import (
                audit_log_create_latency_seconds,
                audit_log_created_total,
            )

            with audit_log_create_latency_seconds.time():
                AuditLog.objects.create(
                    user=user,
                    action=AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE,
                    resource=sender.__name__,
                    content_type=content_type,
                    object_id=str(instance.pk),
                    changes=changes,
                    source="signal",
                )

            audit_log_created_total.labels(
                resource=sender.__name__,
                action="create" if created else "update",
            ).inc()

        except Exception:
            # ✅ metrics fail-safe
            AuditLog.objects.create(
                user=user,
                action=AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE,
                resource=sender.__name__,
                content_type=content_type,
                object_id=str(instance.pk),
                changes=changes,
                source="signal",
            )

    except Exception:
        return


# -------------------------------------------------
# ✅ post_delete with Metrics (SAFE)
# -------------------------------------------------

@receiver(post_delete)
def audit_log_post_delete(sender, instance, **kwargs):
    if _should_skip(sender, **kwargs):
        return

    try:
        user = get_current_user()
        content_type = ContentType.objects.get_for_model(sender)

        try:
            from audit_log.metrics import audit_log_cleanup_total

            AuditLog.objects.create(
                user=user,
                action=AuditLog.Action.DELETE,
                resource=sender.__name__,
                content_type=content_type,
                object_id=str(instance.pk),
                source="signal",
            )

            audit_log_cleanup_total.inc()

        except Exception:
            AuditLog.objects.create(
                user=user,
                action=AuditLog.Action.DELETE,
                resource=sender.__name__,
                content_type=content_type,
                object_id=str(instance.pk),
                source="signal",
            )

    except Exception:
        return
