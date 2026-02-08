# audit_log/admin.py

from django.contrib import admin
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

    # ✅ Step 2.2.2.2 – Admin Optimization
    # حذف N+1 Query در admin list
    list_select_related = ("user", "content_type")

    # جلوگیری از load شدن dropdownهای سنگین
    raw_id_fields = ("user", "content_type")

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
        "changes_formatted",
    ]

    fieldsets = (
        ("Basic Information", {
            "fields": ("id", "timestamp", "action", "resource", "status", "source")
        }),
        ("Description & Object", {
            "fields": ("description", "content_type", "object_id")
        }),
        ("User Information", {
            "fields": ("user",),
            "classes": ("collapse",),
        }),
        ("Changes (JSON)", {
            "fields": ("changes_formatted",),
            "classes": ("collapse", "wide"),
            "description": "Detailed changes made to the object",
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
    user_display.admin_order_field = "user__username"

    # ✅ نمایش نام مدل به شکل خوانا
    def object_model_display(self, obj):
        if obj.content_type:
            model_class = obj.content_type.model_class()
            model_name = model_class.__name__ if model_class else obj.content_type.model
            return f"{obj.content_type.app_label}.{model_name}"
        return "-"

    object_model_display.short_description = "Model"
    object_model_display.admin_order_field = "content_type__model"

    # ✅ نمایش خلاصه description
    def description_short(self, obj):
        if obj.description:
            text = str(obj.description)
            return text[:75] + "..." if len(text) > 75 else text
        return "-"

    description_short.short_description = "Description"
    description_short.admin_order_field = "description"

    # ✅ نمایش فرمت‌شده changes
    def changes_formatted(self, obj):
        if obj.changes:
            try:
                changes_dict = (
                    obj.changes
                    if isinstance(obj.changes, dict)
                    else json.loads(obj.changes)
                )
                formatted = json.dumps(
                    changes_dict,
                    indent=2,
                    ensure_ascii=False,
                )
                return mark_safe(
                    f'<pre style="background:#f5f5f5;'
                    f'padding:10px;border-radius:5px;overflow:auto;">'
                    f'{formatted}</pre>'
                )
            except (json.JSONDecodeError, TypeError):
                return str(obj.changes)
        return "-"

    changes_formatted.short_description = "Changes (Formatted)"

    # ✅ Admin کاملاً Read‑Only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # ✅ غیرفعال کردن bulk actions
    actions = None

    # Pagination
    list_per_page = 50
    show_full_result_count = True
