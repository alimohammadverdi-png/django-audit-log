from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from audit_log.models import AuditLog
from audit_log.api.serializers import AuditLogSerializer
from audit_log.api.authentication import BasicAuth401
from audit_log.api.filters import AuditLogFilter
from audit_log.api.ordering import AuditLogOrderingFilter


class AuditLogViewSet(ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    authentication_classes = [BasicAuth401]
    permission_classes = [IsAuthenticated]

    # ❗ OrderingFilter پیش‌فرض DRF عمداً حذف شده
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        AuditLogOrderingFilter,   # ✅ ONLY custom ordering
    ]

    filterset_class = AuditLogFilter
    search_fields = ["description"]

    # ✅ ORM FIELD — نه API alias
    ordering = ["-timestamp"]

    def get_queryset(self):
        user = self.request.user

        qs = (
            AuditLog.objects
            .select_related("user", "content_type")
            .all()
        )

        # hide noisy system logs
        qs = qs.exclude(
            action="create",
            resource__iexact="user",
        )

        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs
