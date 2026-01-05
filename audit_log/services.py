# audit_log/services.py

from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

def log_action(*, user, action: str, instance, source: str):
    """
    Central service to create an AuditLog entry.
    """
    if not user.is_authenticated:
        # Prevent logging for anonymous users if necessary, 
        # or handle system users differently. For now, assume a logged-in user.
        # This check might need adjustment based on how 'hard_delete' 
        # is called (e.g., if a script calls it without a request user).
        pass

    # Get the content type of the affected instance (e.g., Product)
    content_type = ContentType.objects.get_for_model(instance)

    # Create the log entry
    AuditLog.objects.create(
        user=user,
        action=action,
        source=source,
        content_type=content_type,
        object_id=instance.pk,
    )

    # OPTIONAL: You can return the created log object if needed, 
    # but for simplicity, we keep it as a side-effect function.
