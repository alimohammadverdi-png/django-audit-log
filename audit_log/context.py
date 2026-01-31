# audit_log/context.py

import threading

_thread_locals = threading.local()


def set_current_user(user):
    _thread_locals.user = user


def get_current_user():
    return getattr(_thread_locals, "user", None)


def set_current_request(request):
    _thread_locals.request = request


def get_current_request():
    return getattr(_thread_locals, "request", None)


def clear_context():
    """Clear stored thread-local context (important for cleanup)."""
    for attr in ("user", "request"):
        if hasattr(_thread_locals, attr):
            delattr(_thread_locals, attr)
