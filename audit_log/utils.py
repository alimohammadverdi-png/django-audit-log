# audit_log/utils.py

def calculate_diff(old_obj, new_obj, exclude_fields=None):
    """
    Compare two model instances and return a dict of changed fields.
    """
    exclude_fields = exclude_fields or []

    diff = {}

    for field in new_obj._meta.fields:
        field_name = field.name

        if field_name in exclude_fields:
            continue

        old_value = getattr(old_obj, field_name, None)
        new_value = getattr(new_obj, field_name, None)

        if old_value != new_value:
            diff[field_name] = {
                "old": str(old_value),
                "new": str(new_value),
            }

    return diff if diff else None
