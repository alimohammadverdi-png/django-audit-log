# audit_log/apps.py
import sys
from django.apps import AppConfig


class AuditLogConfig(AppConfig):
    name = "audit_log"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # ⛔ NEVER register signals during setup / tests / migrations
        if any(cmd in sys.argv for cmd in (
            "migrate",
            "makemigrations",
            "test",
            "pytest",
            "collectstatic",
        )):
            return

        from . import signals  # ✅ ONLY place signals are imported
