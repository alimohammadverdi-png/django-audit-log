from django.core.management.base import BaseCommand
from django.db import transaction

from audit_log.models import AuditLog
from audit_log.constants import AUDIT_LOG_RETENTION_DAYS
from audit_log.utils import get_audit_logs_older_than_retention
from audit_log.context import disable_audit_logging


class Command(BaseCommand):
    help = "Delete audit logs older than retention policy"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show how many logs would be deleted",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of rows to delete per batch",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        queryset = get_audit_logs_older_than_retention()
        total = queryset.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("✅ No audit logs to clean up"))
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"🧪 DRY RUN: {total} audit logs would be deleted "
                    f"(older than {AUDIT_LOG_RETENTION_DAYS} days)"
                )
            )
            return

        self.stdout.write(
            f"🧹 Deleting {total} audit logs "
            f"(older than {AUDIT_LOG_RETENTION_DAYS} days)..."
        )

        deleted = 0

        # ⛔ Disable signals during cleanup
        with disable_audit_logging():
            while True:
                ids = list(
                    queryset.values_list("id", flat=True)[:batch_size]
                )
                if not ids:
                    break

                with transaction.atomic():
                    count, _ = AuditLog.objects.filter(id__in=ids).delete()
                    deleted += count

        self.stdout.write(
            self.style.SUCCESS(f"✅ Cleanup completed. Deleted {deleted} audit logs.")
        )
