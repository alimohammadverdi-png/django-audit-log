# audit_log/middleware.py

from audit_log.context import (
    set_current_user,
    set_current_request,
    clear_context,
)


class AuditLogMiddleware:
    """
    Stores request and user in thread-local storage
    for audit logging purposes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # set request context
        set_current_request(request)

        # set user context
        if hasattr(request, "user") and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)

        try:
            response = self.get_response(request)
        finally:
            # VERY IMPORTANT: avoid leaking context between requests
            clear_context()

        return response
