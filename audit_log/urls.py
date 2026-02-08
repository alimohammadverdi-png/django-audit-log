# audit_log/urls.py

from django.urls import path
from .views_metrics import metrics_view

urlpatterns = [
    path("metrics/", metrics_view, name="audit-log-metrics"),
]
