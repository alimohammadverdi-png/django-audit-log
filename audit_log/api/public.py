from typing import Optional, Any
from django.contrib.contenttypes.models import ContentType
from audit_log.models import AuditLog
from audit_log.context import (
    is_audit_logging_disabled,
    get_current_user,
)

def log(
    *,
    action: Optional[str],
    resource: Optional[str] = None,
    user=None,
    instance: Optional[Any] = None,
    status: Optional[str] = None,
    description: Optional[str] = None,
    changes: Optional[dict] = None,
    source: str = "api",
):
    if is_audit_logging_disabled():
        return None

    try:
        user = user or get_current_user()

        content_type = None
        object_id = None

        if instance is not None:
            content_type = ContentType.objects.get_for_model(instance.__class__)
            object_id = str(instance.pk)
            resource = resource or instance.__class__.__name__

        return AuditLog.objects.create(
            user=user,
            action=(action or "unknown").lower(),  # ✅ normalize
            resource=resource or "Unknown",
            status=status or "INFO",
            description=description or "",
            source=source,
            content_type=content_type,
            object_id=object_id,
            changes=changes,
        )
    except Exception:
        return None  # ✅ hard fail‑safe
