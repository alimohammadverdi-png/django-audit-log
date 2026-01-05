import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from audit_log.models import AuditLog
from django.urls import reverse
from datetime import datetime
import pytz

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

@pytest.fixture
def create_audit_logs(normal_user):
    # این تابع چندین لاگ audit با توضیحات مختلف ایجاد می‌کند
    # برای اطمینان از اینکه زمان ایجاد لاگ ها کمی متفاوت است از datetime.now() استفاده می کنیم
    # و سپس یک میکروثانیه به آن اضافه می کنیم.
    # همچنین مطمئن می شویم که timezone aware باشد.
    now = datetime.now(pytz.utc)

    AuditLog.objects.create(
        user=normal_user,
        action="USER_LOGIN",
        resource="User",
        status="SUCCESS",
        description="User logged in successfully.",
        timestamp=now
    )
    AuditLog.objects.create(
        user=normal_user,
        action="PRODUCT_CREATE",
        resource="Product",
        status="SUCCESS",
        description="New product created by admin.",
        timestamp=now.replace(microsecond=now.microsecond + 1 if now.microsecond < 999999 else 0)
    )
    AuditLog.objects.create(
        user=normal_user,
        action="ORDER_UPDATE",
        resource="Order",
        status="FAILED",
        description="Failed to update order status.",
        timestamp=now.replace(microsecond=now.microsecond + 2 if now.microsecond < 999999 else 0)
    )
    AuditLog.objects.create(
        user=normal_user,
        action="USER_LOGOUT",
        resource="User",
        status="SUCCESS",
        description="User logged out.",
        timestamp=now.replace(microsecond=now.microsecond + 3 if now.microsecond < 999999 else 0)
    )
    AuditLog.objects.create(
        user=normal_user,
        action="PRODUCT_VIEW",
        resource="Product",
        status="INFO",
        description="User viewed a product.",
        timestamp=now.replace(microsecond=now.microsecond + 4 if now.microsecond < 999999 else 0)
    )


@pytest.mark.django_db
def test_audit_log_search_by_description(api_client, staff_user, create_audit_logs):
    """
    4.2.3.1 - Test searching audit logs by description (case-insensitive, partial match).
    """
    client = api_client
    client.force_authenticate(user=staff_user) # Staff user can see all logs

    url = reverse("audit-log-list")

    # Test 1: Search for a specific term (e.g., "user")
    response = client.get(url, {"search": "user"})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 3 # Should find "User logged in", "User logged out", "User viewed a product"
    # از "User" در resource و "user" در description استفاده شده است.
    # "User logged in successfully.",
    # "User logged out.",
    # "User viewed a product."
    descriptions = [log['description'] for log in data['results']]
    assert "User logged in successfully." in descriptions
    assert "User logged out." in descriptions
    assert "User viewed a product." in descriptions
    assert "New product created by admin." not in descriptions


    # Test 2: Search for another term (e.g., "product")
    response = client.get(url, {"search": "product"})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2 # Should find "New product created", "User viewed a product"
    descriptions = [log['description'] for log in data['results']]
    assert "New product created by admin." in descriptions
    assert "User viewed a product." in descriptions

    # Test 3: Case-insensitive search (e.g., "fAILED")
    response = client.get(url, {"search": "fAILED"})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1 # Should find "Failed to update order status."
    assert data['results'][0]['description'] == "Failed to update order status."

    # Test 4: Search for a term that does not exist
    response = client.get(url, {"search": "nonexistent"})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 0
