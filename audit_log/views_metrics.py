# audit_log/views_metrics.py

from django.http import HttpResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


def metrics_view(request):
    """
    Expose Prometheus metrics.
    """
    data = generate_latest()
    return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)
