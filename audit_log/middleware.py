from audit_log.utils import set_current_user


class AuditLogUserMiddleware:
    """
    Attach request.user to thread local storage
    so signals can access the current user.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(getattr(request, "user", None))
        try:
            response = self.get_response(request)
        finally:
            set_current_user(None)
        return response
