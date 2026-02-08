import pytest
from audit_log.context import audit_logging_disabled


@pytest.fixture(autouse=True)
def _disable_audit_logging_for_api_tests():
    """
    API tests must not be polluted by model signals/admin side effects.
    Especially: test_api_does_not_allow_creation_of_new_log expects 0 logs.
    """
    with audit_logging_disabled():
        yield
