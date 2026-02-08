from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from audit_log.models import AuditLog
from audit_log.api.serializers import AuditLogSerializer
from audit_log.api.authentication import BasicAuth401


class AuditLogViewSet(ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer

    # ✅ 401 واقعی
    authentication_classes = [BasicAuth401]
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]

    filterset_fields = ["action", "status", "resource"]
    search_fields = ["description"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        user = self.request.user

        qs = (
            AuditLog.objects
            .select_related("user", "content_type")
            .all()
        )

        # ✅ حذف لاگ‌های سیستمی CREATE user
        qs = qs.exclude(
           action__icontains="CREATE",
           resource__iexact="user",
        )

        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs
