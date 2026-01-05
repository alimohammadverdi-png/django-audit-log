# audit_log/admin.py

from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",  # Changed from created_at
        "user",
        "action",
        "resource", # Added new field
        "status",   # Added new field
        "object_model_display",
        "object_id",
        "source",
        "description_short", # Added new field
    )

    list_filter = (
        "action",
        "source",
        "status", # Added new field
        "timestamp",  # Changed from created_at
    )

    search_fields = (
        "object_id",
        "user__username",
        "action", # Added for better searchability
        "resource", # Added for better searchability
        "description", # Added for better searchability
    )

    ordering = ("-timestamp",)  # Changed from created_at

    # ✅ همه فیلدهای دیتابیس فقط‌خواندنی
    # این لیست باید با نام فیلدها در مدل AuditLog مطابقت داشته باشد.
    # به دلیل تغییرات در مدل، بهتر است آن را دوباره تولید کنیم.
    readonly_fields = [field.name for field in AuditLog._meta.fields]
    # اگر نیاز به نمایش content_object در readonly_fields باشد
    # readonly_fields.append('content_object')


    # ✅ نمایش نام مدل به شکل خوانا
    def object_model_display(self, obj):
        # بررسی می‌کنیم که content_type وجود داشته باشد قبل از دسترسی به name
        return obj.content_type.name.title() if obj.content_type else "-"

    object_model_display.short_description = "Model"

    # ✅ نمایش خلاصه description
    def description_short(self, obj):
        return obj.description[:75] + '...' if len(obj.description) > 75 else obj.description
    description_short.short_description = "Description"
    description_short.admin_order_field = 'description' # Allow sorting by full description


    # ✅ کاملاً Read‑Only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
