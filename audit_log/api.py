# audit_log/api.py

from typing import Optional

from audit_log.context import (
    get_current_user,
    get_current_request,
)
from audit_log.models import AuditLog


def log(
    *,
    action: str,
    resource: Optional[str] = None,
    user=None,
    request=None,
    metadata: Optional[dict] = None,
):
    """
    Public API for creating audit log entries.
    Fail-safe by design: never raises.
    """
    try:
        current_user = user or get_current_user()
        current_request = request or get_current_request()

        AuditLog.objects.create(
            action=action,
            resource=resource,
            user=current_user,
            ip_address=getattr(current_request, "META", {}).get("REMOTE_ADDR")
            if current_request
            else None,
            user_agent=getattr(current_request, "META", {}).get("HTTP_USER_AGENT")
            if current_request
            else None,
            metadata=metadata or {},
        )
    except Exception:
        # audit logging must never break the app
        return None
