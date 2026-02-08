from prometheus_client import Counter, Histogram

audit_log_created_total = Counter(
    "audit_log_created_total",
    "Total number of audit logs created",
    ["resource", "action"]
)

audit_log_cleanup_total = Counter(
    "audit_log_cleanup_total",
    "Total number of audit logs cleaned up"
)

audit_log_create_latency_seconds = Histogram(
    "audit_log_create_latency_seconds",
    "Audit log creation latency in seconds"
)
