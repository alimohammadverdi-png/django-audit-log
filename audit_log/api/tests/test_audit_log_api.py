import base64
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient

from audit_log.models import AuditLog


User = get_user_model()


@pytest.mark.django_db
class TestAuditLogAPI:
    def setup_method(self):
        """
        Base setup for all AuditLog API tests
        """
        self.client = APIClient()

        # Create user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        # ContentType for GenericForeignKey
        content_type = ContentType.objects.get_for_model(User)

        # Create audit log (✅ مطابق Model واقعی)
        self.audit_log = AuditLog.objects.create(
            user=self.user,
            action="CREATE",
            source="api",
            content_type=content_type,
            object_id=self.user.id,
            changes={
                "username": [None, "testuser"]
            },
        )

        self.list_url = reverse("audit-log-list")
        self.detail_url = reverse(
            "audit-log-detail",
            args=[self.audit_log.id]
        )

    # ============================
    # 🔒 Unauthenticated tests
    # ============================

    def test_list_unauthenticated_returns_401(self):
        """
        Ensures unauthenticated requests to the list endpoint are rejected with 401.
        """
        response = self.client.get(self.list_url)
        assert response.status_code == 401

    def test_detail_unauthenticated_returns_401(self):
        """
        Ensures unauthenticated requests to the detail endpoint are rejected with 401.
        """
        response = self.client.get(self.detail_url)
        assert response.status_code == 401

    # ============================
    # ✅ Authenticated tests
    # ============================

    def authenticate(self):
        """
        Helper method to authenticate client using BasicAuth
        """
        credentials = base64.b64encode(
            f"{self.user.username}:testpass123".encode()
        ).decode("utf-8")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Basic {credentials}"
        )

    def test_list_authenticated_returns_200(self):
        """
        Ensures authenticated user can access the list endpoint.
        """
        self.authenticate()
        response = self.client.get(self.list_url)
        assert response.status_code == 200

    def test_detail_authenticated_returns_200(self):
        """
        Ensures authenticated user can access the detail endpoint.
        """
        self.authenticate()
        response = self.client.get(self.detail_url)
        assert response.status_code == 200
    
    # ============================
    # 🚫 Read-only tests (405)
    # ============================

    def test_post_not_allowed(self):
        """
        POST should not be allowed on AuditLog API
        """
        self.authenticate()
        response = self.client.post(self.list_url, data={})
        assert response.status_code == 405

    def test_put_not_allowed(self):
        """
        PUT should not be allowed on AuditLog API
        """
        self.authenticate()
        response = self.client.put(
            self.detail_url,
            data={"action": "UPDATE"},
        )
        assert response.status_code == 405

    def test_patch_not_allowed(self):
        """
        PATCH should not be allowed on AuditLog API
        """
        self.authenticate()
        response = self.client.patch(
            self.detail_url,
            data={"action": "UPDATE"},
        )
        assert response.status_code == 405

    def test_delete_not_allowed(self):
        """
        DELETE should not be allowed on AuditLog API
        """
        self.authenticate()
        response = self.client.delete(self.detail_url)
        assert response.status_code == 405
