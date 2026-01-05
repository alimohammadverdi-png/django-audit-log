from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        """
        Soft delete: set deleted_at instead of real DELETE
        """
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        """
        Real delete from database (dangerous)
        """
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)
    
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(
            self.model,
            using=self._db
        ).alive()

    def hard_delete(self):
        return self.get_queryset().hard_delete()
       

class AuditModel(models.Model):
    """
    Base abstract model for:
    - audit fields
    - soft delete support
    """


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_set'
    )

    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_%(class)s_set'
    )
    
    # ✅ Soft Delete (Step 6.3)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
    
# ✅ FIX: instance-level soft delete
    def delete(self, using=None, keep_parents=False):
        if self.deleted_at is None:
            self.deleted_at = timezone.now()
            self.save(update_fields=["deleted_at"])

    # ✅ instance-level hard delete
    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)
    
    # ✅ Restore (Undo Soft Delete)
    def restore(self):
        if self.deleted_at is not None:
            self.deleted_at = None
            self.save(update_fields=['deleted_at'])
            