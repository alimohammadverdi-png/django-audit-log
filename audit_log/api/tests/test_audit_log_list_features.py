import base64
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient

from audit_log.models import AuditLog

User = get_user_model()

@pytest.mark.django_db
class TestAuditLogListFeatures:
    """
    تست قابلیت لیست: pagination, filtering, ordering
    """

    def setup_method(self):
        self.client = APIClient()

        # ایجاد کاربر
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        # احراز هویت
        credentials = base64.b64encode(
            b"testuser:testpass123"
        ).decode("utf-8")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Basic {credentials}"
        )
        # آدرس API
        self.url = reverse("audit-log-list")
        # ContentType
        content_type = ContentType.objects.get_for_model(User)
        # ایجاد لاگ CREATE و UPDATE
        for i in range(5):
            AuditLog.objects.create(
                user=self.user,
                action="CREATE",
                source="api",
                content_type=content_type,
                object_id=self.user.id,
                changes={"index": i},
            )
        for i in range(5):
            AuditLog.objects.create(
                user=self.user,
                action="UPDATE",
                source="api",
                content_type=content_type,
                object_id=self.user.id,
                changes={"index": i},
            )

    def test_list_is_paginated(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "results" in data

    def test_filter_by_action(self):
        response = self.client.get(f"{self.url}?action=CREATE")
        assert response.status_code == 200
        for item in response.json()["results"]:
            assert item["action"] == "CREATE"

    def test_ordering_by_created_at_desc(self):
        response = self.client.get(f"{self.url}?ordering=-created_at")
        assert response.status_code == 200
