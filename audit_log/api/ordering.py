from rest_framework.filters import OrderingFilter


class AuditLogOrderingFilter(OrderingFilter):
    def remove_invalid_fields(self, queryset, ordering, view, request):
        mapped = []

        for term in ordering:
            desc = term.startswith("-")
            field = term.lstrip("-")

            # ✅ API alias → DB field
            if field == "created_at":
                field = "timestamp"

            mapped.append(f"-{field}" if desc else field)

        return super().remove_invalid_fields(
            queryset, mapped, view, request
        )
