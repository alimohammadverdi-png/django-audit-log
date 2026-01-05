from rest_framework.routers import DefaultRouter
from audit_log.api.views import AuditLogViewSet

# تعریف روتر DRF
router = DefaultRouter()
# ثبت ViewSet
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

# URL Patterns نهایی
urlpatterns = router.urls
