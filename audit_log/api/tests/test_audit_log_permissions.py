import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from audit_log.models import AuditLog
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


@pytest.mark.django_db
class TestAuditLogPermissions:

    def setup_method(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username="user1", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="pass123"
        )
        self.staff = User.objects.create_user(
            username="staff", password="pass123", is_staff=True
        )

        content_type = ContentType.objects.get_for_model(User)

        self.log_user1 = AuditLog.objects.create(
            user=self.user1,
            action="login",
            source="api",
            content_type=content_type,
            object_id=self.user1.id,
            changes={"email": ["old", "new"]},
        )

        self.log_user2 = AuditLog.objects.create(
            user=self.user2,
            action="logout",
            source="api",
            content_type=content_type,
            object_id=self.user2.id,
            changes={"status": ["on", "off"]},
        )

    def test_normal_user_list_only_own_logs(self):
        self.client.force_authenticate(user=self.user1)

        url = reverse("audit-log-list")
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == self.log_user1.id

    def test_normal_user_cannot_access_other_users_log_detail(self):
        self.client.force_authenticate(user=self.user1)

        url = reverse("audit-log-detail", args=[self.log_user2.id])
        response = self.client.get(url)

        assert response.status_code in (403, 404)

    def test_staff_user_can_see_all_logs(self):
        self.client.force_authenticate(user=self.staff)

        url = reverse("audit-log-list")
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 2

    def test_staff_user_can_access_any_log_detail(self):
        self.client.force_authenticate(user=self.staff)

        url = reverse("audit-log-detail", args=[self.log_user1.id])
        response = self.client.get(url)

        assert response.status_code == 200
