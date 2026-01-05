# audit_log/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import connection, utils as db_utils # db_utils برای مدیریت خطاها
import json

from audit_log.models import AuditLog


# -------------------------------------------------
# ابزار کمکی: بررسی آماده بودن Schema (وجود ستون‌های جدید)
# -------------------------------------------------
def audit_log_schema_is_ready() -> bool:
    """
    Checks if the AuditLog table exists AND has the 'resource' column, 
    preventing issues during migration/test setup when the table exists 
    but is in an older schema state.
    """
    try:
        table_name = AuditLog._meta.db_table
        
        # 1. آیا جدول اصلاً وجود دارد؟
        if table_name not in connection.introspection.table_names():
            return False

        # 2. آیا ستون‌های جدید وجود دارند؟ (استفاده از PRAGMA table_info برای SQLite)
        with connection.cursor() as cursor:
            # PRAGMA table_info به ما لیستی از ستون‌های جدول را می‌دهد
            cursor.execute(f"PRAGMA table_info({table_name})")
            # ستون دوم (index 1) نام ستون است.
            columns = [col[1] for col in cursor.fetchall()] 
            
        # چک می‌کنیم که ستون 'resource' به عنوان یک ستون حیاتی از فاز جدید، وجود داشته باشد.
        return "resource" in columns
        
    except db_utils.OperationalError:
        # اگر در حین چک کردن خطا رخ داد (مثلاً اتصال هنوز برقرار نیست)
        return False
    except Exception:
        # برای هر خطای غیرمنتظره دیگر
        return False


# -------------------------------------------------
# DELETE signal
# -------------------------------------------------
@receiver(post_delete)
def audit_log_delete_signal_receiver(sender, instance, **kwargs):
    # 1️⃣ جلوگیری از لاگ کردن در زمان migrate / loaddata
    if kwargs.get("raw"):
        return

    # 2️⃣ جلوگیری از حلقه بی‌نهایت
    if sender == AuditLog:
        return

    # 3️⃣ اگر جدول هنوز ساخته نشده یا schema قدیمی است
    # ما از تابع جدید و مطمئن‌تر استفاده می‌کنیم
    if not audit_log_schema_is_ready():
        return

    # 4️⃣ امکان غیرفعال‌سازی دستی
    if hasattr(instance, "_audit_log_enabled") and not instance._audit_log_enabled:
        return

    user = getattr(instance, "updated_by", None)
    if not user and hasattr(instance, "owner"):
        user = instance.owner

    try:
        content_type = ContentType.objects.get_for_model(sender)

        AuditLog.objects.create(
            user=user,
            action="delete",
            source="signal",
            content_type=content_type,
            object_id=instance.pk,
            changes=None,
            timestamp=timezone.now(),

            resource=sender._meta.model_name,
            status="INFO",
            description=f"{sender.__name__} deleted (id={instance.pk})",
        )
    except Exception:
        # در سیگنال هرگز نباید سیستم را بخوابانیم (به خصوص در محیط تست)
        pass


# -------------------------------------------------
# SAVE signal (create / update)
# -------------------------------------------------
@receiver(post_save)
def audit_log_save_signal_receiver(sender, instance, created, **kwargs):
    # 1️⃣ جلوگیری از لاگ کردن در زمان migrate / loaddata
    if kwargs.get("raw"):
        return

    # 2️⃣ جلوگیری از حلقه بی‌نهایت
    if sender == AuditLog:
        return

    # 3️⃣ اگر جدول هنوز ساخته نشده یا schema قدیمی است
    if not audit_log_schema_is_ready():
        return

    # 4️⃣ امکان غیرفعال‌سازی دستی
    if hasattr(instance, "_audit_log_enabled") and not instance._audit_log_enabled:
        return

    action_type = "create" if created else "update"

    user = getattr(instance, "updated_by", None)
    if not user and hasattr(instance, "owner"):
        user = instance.owner

    try:
        content_type = ContentType.objects.get_for_model(sender)

        AuditLog.objects.create(
            user=user,
            action=action_type,
            source="signal",
            content_type=content_type,
            object_id=instance.pk,
            changes=None,
            timestamp=timezone.now(),

            resource=sender._meta.model_name,
            status="INFO",
            description=f"{sender.__name__} {action_type} (id={instance.pk})",
        )
    except Exception:
        # سیگنال نباید باعث fail شدن تست‌ها شود
        pass
