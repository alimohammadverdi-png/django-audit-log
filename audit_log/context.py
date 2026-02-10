from contextlib import contextmanager
from threading import local
from contextvars import ContextVar
from typing import Optional

# -----------------------------------------
# 🧠 Internal thread / async context state
# -----------------------------------------
_state = local()

# Async + thread-safe correlation id
_correlation_id: ContextVar[Optional[str]] = ContextVar(
    "correlation_id",
    default=None,
)

# -----------------------------------------
# 👤 user / request
# -----------------------------------------
def set_current_user(user):
    """Store the currently authenticated user in thread-local state."""
    _state.user = user


def get_current_user():
    """Return the current user if available, else None."""
    return getattr(_state, "user", None)


def set_current_request(request):
    """Store the current HTTP request in thread-local state."""
    _state.request = request


def get_current_request():
    """Return the current HTTP request if available, else None."""
    return getattr(_state, "request", None)


def clear_context():
    """
    Clear all stored context safely.
    This is critical for test isolation and migrations.
    """
    for attr in ("user", "request", "audit_disabled"):
        if hasattr(_state, attr):
            delattr(_state, attr)

    # Reset correlation id safely
    try:
        _correlation_id.set(None)
    except LookupError:
        pass


# -----------------------------------------
# 🔕 audit logging switch
# -----------------------------------------
def is_audit_logging_disabled() -> bool:
    """Check whether audit log recording is temporarily disabled."""
    return getattr(_state, "audit_disabled", False)


def disable_audit_logging():
    """Temporarily disable audit log recording."""
    _state.audit_disabled = True


def enable_audit_logging():
    """Re-enable audit log recording."""
    _state.audit_disabled = False


@contextmanager
def audit_logging_disabled():
    """
    Context manager for safely disabling audit logging.
    Always restores previous state.
    """
    previous = is_audit_logging_disabled()
    _state.audit_disabled = True
    try:
        yield
    finally:
        _state.audit_disabled = previous


# -----------------------------------------
# 🔗 correlation id
# -----------------------------------------
def set_correlation_id(value: Optional[str]):
    """Set or override the current correlation id."""
    _correlation_id.set(value)


def get_correlation_id() -> Optional[str]:
    """Return the current correlation id if set, else None."""
    return _correlation_id.get()
