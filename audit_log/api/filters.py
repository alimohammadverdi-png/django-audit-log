import django_filters
from audit_log.models import AuditLog


class AuditLogFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name="user__id")

    action = django_filters.CharFilter(method="filter_action")

    content_type = django_filters.CharFilter(
        field_name="content_type__model",
        lookup_expr="iexact",
    )

    object_id = django_filters.CharFilter(
        field_name="object_id",
        lookup_expr="exact",
    )

    # ✅ API created_at → DB timestamp
    created_at__gte = django_filters.DateTimeFilter(
        field_name="timestamp",
        lookup_expr="gte",
    )

    created_at__lte = django_filters.DateTimeFilter(
        field_name="timestamp",
        lookup_expr="lte",
    )

    class Meta:
        model = AuditLog
        fields = [
            "user",
            "action",
            "content_type",
            "object_id",
            "created_at__gte",
            "created_at__lte",
        ]

    def filter_action(self, queryset, name, value):
        if not value:
            return queryset

        normalized = value.lower()

        valid_actions = {
            choice[0]
            for choice in AuditLog._meta.get_field("action").choices
        }

        if normalized not in valid_actions:
            return queryset.none()

        return queryset.filter(action=normalized)
