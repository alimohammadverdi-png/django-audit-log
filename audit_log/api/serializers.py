from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from audit_log.models import AuditLog

User = get_user_model()


class UserReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")
        read_only_fields = fields


class ContentTypeReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ("id", "app_label", "model")
        read_only_fields = fields


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for AuditLog API
    Fully aligned with Phase 4.2 Contract
    """

    user = UserReadOnlySerializer(read_only=True)
    content_type = ContentTypeReadOnlySerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "user",
            "action",
            "resource",       # ✅ جدید
            "status",         # ✅ جدید
            "description",    # ✅ حیاتی برای search
            "source",
            "content_type",
            "object_id",
            "changes",
            "timestamp",      # ✅ جایگزین created_at
        )
        read_only_fields = fields

