from rest_framework.filters import OrderingFilter


class AuditLogOrderingFilter(OrderingFilter):
    ordering_param = "ordering"

    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get(self.ordering_param)

        # ✅ default
        if not ordering:
            return queryset.order_by("-timestamp")

        if ordering == "created_at":
            return queryset.order_by("timestamp")

        if ordering == "-created_at":
            return queryset.order_by("-timestamp")

        # ⛔ NEVER pass unknown fields to ORM
        return queryset.order_by("-timestamp")
