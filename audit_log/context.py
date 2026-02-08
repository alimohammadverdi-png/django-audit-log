from contextlib import contextmanager
from threading import local

_state = local()

# ---------- request / user ----------
def set_current_user(user):
    _state.user = user

def get_current_user():
    return getattr(_state, "user", None)

def set_current_request(request):
    _state.request = request

def get_current_request():
    return getattr(_state, "request", None)

def clear_context():
    _state.user = None
    _state.request = None

# ---------- audit logging switch ----------
def is_audit_logging_disabled():
    return getattr(_state, "audit_disabled", False)

def disable_audit_logging():
    _state.audit_disabled = True

def enable_audit_logging():
    _state.audit_disabled = False

@contextmanager
def audit_logging_disabled():
    disable_audit_logging()
    try:
        yield
    finally:
        enable_audit_logging()
