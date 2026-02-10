from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from django.apps import apps
from django.db import connection

from common.models import AuditModel
from audit_log.models import AuditLog
from audit_log.utils import get_current_user


User = settings.AUTH_USER_MODEL


def _auditlog_table_exists():
    try:
        return "audit_log_auditlog" in connection.introspection.table_names()
    except Exception:
        return False


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام دسته")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="نامک (Slug)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(AuditModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="دسته"
    )
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قیمت")
    stock = models.PositiveIntegerField(verbose_name="موجودی")
    sku = models.CharField(max_length=50, unique=True, verbose_name="کد محصول (SKU)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_products",
        editable=False,
        verbose_name="مالک"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products_created"
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products_updated"
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    # ✅ FINAL: Soft delete + audit log (migration & test safe)
    def delete(self, using=None, keep_parents=False):
        if self.deleted_at:
            return

        # ⛔️ migrate / startup safety
        if not apps.ready or not _auditlog_table_exists():
            self.deleted_at = timezone.now()
            self.save(update_fields=["deleted_at"])
            return

        try:
            AuditLog.objects.create(
                user=get_current_user(),
                action="delete",
                resource="Product",
                content_type=None,
                object_id=str(self.pk),
                source="model",
                changes={"soft": True},
            )
        except Exception:
            pass

        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
