from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .models import Category, Product
from audit_log.models import AuditLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "price",
        "stock",
        "is_active",
        "created_at",
        "deleted_at",
    )
    search_fields = ("name", "sku")
    list_filter = ("is_active", "category")

    actions = (
        "bulk_deactivate_products",
        "bulk_soft_delete_products",
    )

    def _require_superuser(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied

    def _bulk_log(self, *, request, action, changes):
        AuditLog.objects.create(
            user=request.user,
            action=action,
            resource="Product",
            content_type=ContentType.objects.get_for_model(Product),
            object_id=None,
            source="admin",
            changes=changes,
        )

    def bulk_deactivate_products(self, request, queryset):
        self._require_superuser(request)

        queryset = queryset.all()
        ids = list(queryset.values_list("id", flat=True))

        before = list(queryset.values("id", "is_active"))

        queryset.update(is_active=False, updated_by=request.user)

        if ids:
            self._bulk_log(
                request=request,
                action="bulk_update",
                changes={
                    "ids": ids,
                    "before": before,
                    "after": {"is_active": False},
                },
            )

    def bulk_soft_delete_products(self, request, queryset):
        self._require_superuser(request)

        queryset = queryset.all()
        ids = list(queryset.values_list("id", flat=True))

        queryset.update(deleted_at=timezone.now(), updated_by=request.user)

        if ids:
            self._bulk_log(
                request=request,
                action="bulk_delete",
                changes={
                    "ids": ids,
                    "count": len(ids),
                    "soft": True,
                },
            )

    def delete_queryset(self, request, queryset):
        self.bulk_soft_delete_products(request, queryset)
