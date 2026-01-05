import django_filters
from audit_log.models import AuditLog

class AuditLogFilter(django_filters.FilterSet):
    # فیلتر بر اساس user_id (برای راحتی)
    user = django_filters.NumberFilter(field_name='user__id')

    # فیلتر بر اساس نام کامل اکشن (READ, CREATE, UPDATE, DELETE)
    action = django_filters.CharFilter(field_name='action')
    
    # فیلتر بر اساس نام ContentType (مثلاً 'products.product')
    content_type = django_filters.CharFilter(
        field_name='content_type__model',
        lookup_expr='iexact'
    )

    # فیلتر برای تاریخ/زمان (Greater Than or Equal to)
    created_at__gte = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    
    # فیلتر برای تاریخ/زمان (Less Than or Equal to)
    created_at__lte = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    class Meta:
        model = AuditLog
        fields = [
            'user', 
            'action', 
            'content_type', 
            'object_id',
            'created_at__gte',
            'created_at__lte',
        ]
