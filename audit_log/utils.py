import threading
from typing import Optional
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from audit_log.constants import IGNORED_FIELDS, AUDIT_LOG_RETENTION_DAYS
from audit_log.models import AuditLog


User = get_user_model()
_thread_locals = threading.local()


# =========================
# Current User (Thread Local)
# =========================

def set_current_user(user: Optional[User]) -> None:
    """
    Store current user in thread local storage.
    Used by middleware.
    """
    _thread_locals.user = user


def get_current_user() -> Optional[User]:
    """
    Safely get current user from thread local storage.
    Returns None if not set.
    """
    return getattr(_thread_locals, "user", None)


# =========================
# Changes Diff (Phase 2.1)
# =========================

def compute_changes(before: dict | None, after: dict | None) -> dict:
    """
    Compute meaningful changes between two state dicts.
    Returns empty dict if no meaningful change exists.
    """
    if not before or not after:
        return {}

    changes = {}

    for field, old_value in before.items():
        if field in IGNORED_FIELDS:
            continue

        new_value = after.get(field)
        if old_value != new_value:
            changes[field] = {
                "before": old_value,
                "after": new_value,
            }

    return changes


# =========================
# Retention Policy (Phase 2.3)
# =========================

def get_audit_logs_older_than_retention(days: int | None = None):
    """
    Returns queryset of audit logs older than retention window.

    ⚠️ IMPORTANT:
    - This function DOES NOT delete anything.
    - Safe to use in tests, admin, and management commands.
    """
    retention_days = days or AUDIT_LOG_RETENTION_DAYS
    cutoff = timezone.now() - timedelta(days=retention_days)

    return AuditLog.objects.filter(timestamp__lt=cutoff)
