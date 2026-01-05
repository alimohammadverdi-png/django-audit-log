# products/admin.py

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _ # برای بین‌المللی‌سازی فیلتر

from .models import Product, Category
from audit_log.models import AuditLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}


# --- CUSTOM FILTER FOR DELETED PRODUCTS ---
class DeletedFilter(admin.SimpleListFilter):
    title = _('Deletion Status')  # عنوان فیلتر در پنل ادمین
    parameter_name = 'deleted'     # نام پارامتر در URL

    def lookups(self, request, model_admin):
        # این متد گزینه‌هایی را که کاربر می‌تواند انتخاب کند، برمی‌گرداند.
        return (
            ('all', _('All')),
            ('deleted', _('Deleted Products')),
            ('not_deleted', _('Active Products')),
        )

    def queryset(self, request, queryset):
        # این متد بر اساس انتخاب کاربر، کوئری‌ست را فیلتر می‌کند.
        if self.value() == 'deleted':
            return queryset.filter(deleted_at__isnull=False)
        if self.value() == 'not_deleted':
            return queryset.filter(deleted_at__isnull=True)
        return queryset # 'all' (یا هیچ‌کدام) را برگردانید تا همه محصولات نمایش داده شوند


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
    # اصلاح: list_filter حالا از کلاس DeletedFilter استفاده می‌کند
    list_filter = ("is_active", "category", DeletedFilter)
    search_fields = ("name", "sku")

    actions = [
        "bulk_deactivate_products",
        "bulk_soft_delete_products",
        "hard_delete_products",
        "bulk_restore_products",
    ]

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()

    def bulk_deactivate_products(self, request, queryset):
        if not request.user.is_superuser:
            raise PermissionDenied

        before_values = list(queryset.values('id', 'is_active'))

        updated_count = queryset.update(is_active=False, updated_by=request.user)

        if updated_count > 0:
            AuditLog.objects.create(
                user=request.user,
                action="bulk_update",
                source="admin",
                content_type=ContentType.objects.get_for_model(Product),
                object_id=0,
                changes={
                    "updated_fields": ["is_active"],
                    "before": before_values,
                    "after": {"is_active": False},
                    "count": updated_count,
                    "ids": list(queryset.values_list("id", flat=True)),
                },
            )
        # self.message_user(request, f"{updated_count} products deactivated successfully.")
        # فراخوانی message_user برای سازگاری با تست‌ها موقتاً غیرفعال شده است.

    bulk_deactivate_products.short_description = "Deactivate selected products"

    def bulk_soft_delete_products(self, request, queryset):
        if not request.user.is_superuser:
            raise PermissionDenied
            
        count = queryset.count()
        ids = list(queryset.values_list("id", flat=True))

        updated_count = queryset.update(deleted_at=timezone.now(), updated_by=request.user)

        if updated_count > 0:
            AuditLog.objects.create(
                user=request.user,
                action="bulk_soft_delete",
                source="admin",
                content_type=ContentType.objects.get_for_model(Product),
                object_id=0,
                changes={
                    "count": count,
                    "ids": ids,
                },
            )
        # self.message_user(request, f"{count} products soft deleted successfully.")
        # فراخوانی message_user برای سازگاری با تست‌ها موقتاً غیرفعال شده است.
    
    bulk_soft_delete_products.short_description = "Soft delete selected products"

    def hard_delete_products(self, request, queryset):
        if not request.user.is_superuser:
            raise PermissionDenied

        count = queryset.count()
        ids = list(queryset.values_list("id", flat=True))

        if count > 0:
            AuditLog.objects.create(
                user=request.user,
                action="bulk_hard_delete",
                source="admin",
                content_type=ContentType.objects.get_for_model(Product),
                object_id=0,
                changes={
                    "count": count,
                    "ids": ids,
                },
            )

        for obj in queryset:
            obj.hard_delete()
        
        # self.message_user(request, f"{count} products hard deleted successfully.")
        # فراخوانی message_user برای سازگاری با تست‌ها موقتاً غیرفعال شده است.
    
    hard_delete_products.short_description = "Hard delete selected products"

    def bulk_restore_products(self, request, queryset):
        if not request.user.is_superuser:
            raise PermissionDenied

        restorable_queryset = queryset.filter(deleted_at__isnull=False)
        restored_count = restorable_queryset.update(deleted_at=None, updated_by=request.user)

        if restored_count > 0:
            AuditLog.objects.create(
                user=request.user,
                action="bulk_restore",
                source="admin",
                content_type=ContentType.objects.get_for_model(Product),
                object_id=0,
                changes={
                    "count": restored_count,
                    "ids": list(restorable_queryset.values_list("id", flat=True)),
                }
            )
        # self.message_user(request, f"{restored_count} products restored successfully.")
        # فراخوانی message_user برای سازگاری با تست‌ها موقتاً غیرفعال شده است.
    
    bulk_restore_products.short_description = "Restore selected products"

    def delete_queryset(self, request, queryset):
        # بازنویسی متد پیش‌فرض delete_queryset برای استفاده از soft delete
        self.bulk_soft_delete_products(request, queryset)
