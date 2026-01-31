# audit_log/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user_display",
        "action",
        "resource",
        "status",
        "object_model_display",
        "object_id",
        "source",
        "description_short",
    )

    list_filter = (
        "action",
        "source",
        "status",
        "timestamp",
    )

    search_fields = (
        "object_id",
        "user__username",
        "action",
        "resource",
        "description",
    )

    ordering = ("-timestamp",)

    # فیلدهای اصلی مدل که باید read-only باشند
    readonly_fields = [
        "id",
        "timestamp",
        "user",
        "action",
        "resource",
        "status",
        "description",
        "source",
        "content_type",
        "object_id",
        "changes",
        "changes_formatted",  # نمایش فرمت شده changes
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'timestamp', 'action', 'resource', 'status', 'source')
        }),
        ('Description & Object', {
            'fields': ('description', 'content_type', 'object_id')
        }),
        ('User Information', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Changes (JSON)', {
            'fields': ('changes_formatted',),
            'classes': ('collapse', 'wide'),
            'description': 'Detailed changes made to the object'
        }),
    )

    # ✅ نمایش ایمن user در لیست
    def user_display(self, obj):
        if obj.user:
            full_name = obj.user.get_full_name()
            if full_name:
                return f"{obj.user.username} ({full_name})"
            return obj.user.username
        return "system"
    user_display.short_description = "User"
    user_display.admin_order_field = 'user__username'

    # ✅ نمایش نام مدل به شکل خوانا در لیست
    def object_model_display(self, obj):
        if obj.content_type:
            # استفاده از verbose_name اگر موجود باشد
            model_name = obj.content_type.model_class().__name__ if obj.content_type.model_class() else obj.content_type.model
            app_label = obj.content_type.app_label
            return f"{app_label}.{model_name}"
        return "-"
    object_model_display.short_description = "Model"
    object_model_display.admin_order_field = 'content_type__model'

    # ✅ نمایش خلاصه description در لیست
    def description_short(self, obj):
        if obj.description:
            text = str(obj.description)
            if len(text) > 75:
                return text[:75] + '...'
            return text
        return "-"
    description_short.short_description = "Description"
    description_short.admin_order_field = 'description'

    # ✅ نمایش فرمت شده changes (فقط برای نمایش در فرم)
    def changes_formatted(self, obj):
        if obj.changes:
            try:
                # تلاش برای نمایش JSON به صورت فرمت شده
                changes_dict = obj.changes if isinstance(obj.changes, dict) else json.loads(obj.changes)
                formatted = json.dumps(changes_dict, indent=2, ensure_ascii=False)
                return mark_safe(f'<pre style="background:#f5f5f5;padding:10px;border-radius:5px;overflow:auto;">{formatted}</pre>')
            except (json.JSONDecodeError, TypeError):
                return str(obj.changes)
        return "-"
    changes_formatted.short_description = "Changes (Formatted)"

    # ✅ کاملاً Read‑Only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # غیرفعال کردن actions در لیست
    actions = None

    # بهبود عملکرد جستجو برای نمایش تعداد زیادی رکورد
    list_per_page = 50
    show_full_result_count = True

    # نمایش timestamp به صورت human-readable در لیست
    def timestamp_display(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_display.short_description = "Timestamp"
    timestamp_display.admin_order_field = 'timestamp'
