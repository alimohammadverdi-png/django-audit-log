import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from audit_log.models import AuditLog
from django.urls import reverse  # این ایمپورت قبلاً توسط شما اضافه شده بود و درست است

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_user():
    return User.objects.create_user(
        username="staff_user", password="password", is_staff=True
    )


@pytest.fixture
def normal_user():
    return User.objects.create_user(username="normal_user", password="password")


@pytest.mark.django_db
def test_api_does_not_allow_creation_of_new_log(api_client, staff_user, normal_user):
    """
    4.2.2.1 - Test that POST requests to the AuditLog list endpoint are forbidden.
    The primary way to create an AuditLog must be through signals, not the API.
    Expected: 405 Method Not Allowed.
    """
    client = api_client
    client.force_authenticate(user=normal_user)

    # 1. Prepare dummy data
    dummy_payload = {
        "user": normal_user.id,
        "action": "DUMMY_ACTION",
        "resource": "DUMMY_RESOURCE",
        "status": "OK",
        "description": "Attempt to create log via API.",
    }

    # 2. Attempt to POST
    # اینجا URL را با استفاده از reverse می‌سازیم تا از صحت مسیر مطمئن شویم
    url = reverse("audit-log-list") # <-- این خط اصلاح شده است
    response = client.post(url, dummy_payload, format="json")

    # 3. Assertions
    # The API should strictly forbid creation (405 due to ReadOnlyModelViewSet)
    assert response.status_code == 405
    # Database check: no new log should be created
    assert AuditLog.objects.count() == 0
