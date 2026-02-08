from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed


class BasicAuth401(BasicAuthentication):
    """Force DRF to return HTTP 401 instead of 403."""
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            raise
        except Exception:
            raise AuthenticationFailed("Authentication credentials were not provided.")
