import uuid

from audit_log.context import (
    set_current_user,
    set_current_request,
    clear_context,
    set_correlation_id,
)


class AuditLogContextMiddleware:
    """
    Middleware for:
    - Storing current user & request in context
    - Generating / propagating Correlation ID
    - Cleaning context after response
    """

    HEADER_NAME = "HTTP_X_CORRELATION_ID"
    RESPONSE_HEADER = "X-Correlation-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ---------- Correlation ID ----------
        correlation_id = request.META.get(self.HEADER_NAME)
        if not correlation_id:
            correlation_id = uuid.uuid4().hex

        set_correlation_id(correlation_id)
        request.correlation_id = correlation_id

        # ---------- User / Request ----------
        set_current_user(getattr(request, "user", None))
        set_current_request(request)

        try:
            response = self.get_response(request)
        finally:
            clear_context()

        # ---------- Response header ----------
        response[self.RESPONSE_HEADER] = correlation_id
        return response
