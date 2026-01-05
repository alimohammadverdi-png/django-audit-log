from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from audit_log.models import AuditLog
from audit_log.api.serializers import AuditLogSerializer


class AuditLogViewSet(ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 1. Base QuerySet + Ordering
        qs = AuditLog.objects.all().order_by("-timestamp")

        # 2. Permission Logic (Phase 4.2.1)
        if not user.is_staff:
            qs = qs.filter(user=user)

        # 3. Search Logic (Phase 4.2.3)
        search_term = self.request.query_params.get("search")
        if search_term:
            qs = qs.filter(
                description__isnull=False,
                description__icontains=search_term,
            ).exclude(
                # ✅ فقط حذف لاگ‌های سیستمی ساخت USER
                action__icontains="CREATE",
                resource__iexact="user",
            )

        return qs
