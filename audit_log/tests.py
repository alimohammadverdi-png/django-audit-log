import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from audit_log.api import log
from audit_log.models import AuditLog
from audit_log.utils import compute_changes

User = get_user_model()


@pytest.mark.django_db
def test_log_without_user_and_request():
    """
    log() should work without user or request (fail-safe behavior)
    """
    log(
        action=AuditLog.Action.CREATE,
        description="Test log without context",
    )

    assert AuditLog.objects.count() == 1

    audit = AuditLog.objects.first()
    assert audit.user is None
    assert audit.description == "Test log without context"


@pytest.mark.django_db
def test_log_with_instance_resolves_content_type_and_object_id():
    """
    log() should resolve content_type and object_id from instance
    """
    user = User.objects.create_user(
        username="testuser",
        password="password123"
    )

    log(
        action=AuditLog.Action.CREATE,
        instance=user,
        description="User created",
    )

    audit = AuditLog.objects.first()

    assert audit.object_id == str(user.pk)
    assert audit.content_type == ContentType.objects.get_for_model(User)
    assert audit.description == "User created"


@pytest.mark.django_db
def test_log_fail_safe_on_invalid_input():
    """
    log() must not raise exception on invalid input
    """
    try:
        log(
            action=None,  # invalid on purpose
            description="This should not crash",
        )
    except Exception as exc:
        pytest.fail(f"log() raised exception: {exc}")

    # Either 0 or 1 log is acceptable — important part is no crash
    assert AuditLog.objects.count() in (0, 1)




def test_compute_changes_detects_real_change():
    before = {"price": 100}
    after = {"price": 120}

    assert compute_changes(before, after) == {
        "price": {"before": 100, "after": 120}
    }


def test_compute_changes_ignores_updated_at():
    before = {"updated_at": "2024-01-01T12:00"}
    after = {"updated_at": "2024-01-02T12:00"}

    assert compute_changes(before, after) == {}


def test_compute_changes_returns_empty_if_no_change():
    before = {"name": "A", "price": 10}
    after = {"name": "A", "price": 10}

    assert compute_changes(before, after) == {}
