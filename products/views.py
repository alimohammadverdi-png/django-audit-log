from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

from accounts.permissions.object_permissions import IsOwnerOrAdmin
from common.views import OwnedModelViewSet
from audit_log.services import log_action


# ==========================
# Category
# ==========================
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]


# ==========================
# Product
# ==========================
class ProductViewSet(OwnedModelViewSet):
    """
    Product API
    - CRUD: Owner or Admin
    - Soft Delete: Owner or Admin
    - Restore: Admin / Superuser only
    - Hard Delete: Admin / Superuser only
    - Default: hides deleted items
    """

    queryset = Product.all_objects.all()
    serializer_class = ProductSerializer

    permission_classes = [
        IsAuthenticated,
        IsOwnerOrAdmin,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = {
        "price": ["gte", "lte"],
        "stock": ["gte", "lte"],
        "category": ["exact"],
    }

    search_fields = ["name", "sku"]
    ordering_fields = ["price", "stock", "created_at"]
    ordering = ["-created_at"]

    # ==========================
    # QuerySet Logic
    # ==========================
    def get_queryset(self):
        """
        - Default: only active products
        - Admin + ?deleted=true: only deleted products
        - Owner filtering is inherited from OwnedModelViewSet
        """
        queryset = super().get_queryset()

        user = self.request.user
        show_deleted = self.request.query_params.get("deleted", "false").lower() == "true"

        if show_deleted and (user.is_staff or user.is_superuser):
            return queryset.filter(deleted_at__isnull=False)

        return queryset.filter(deleted_at__isnull=True)

    # ==========================
    # Soft Delete
    # ==========================
    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        product = self.get_object()
        product.delete()

        log_action(
            user=request.user,
            action="soft_delete",
            instance=product,
            source="api",
        )

        return Response(
            {"detail": "Product soft deleted successfully."},
            status=status.HTTP_200_OK,
        )

    # ==========================
    # Restore (Admin only)
    # ==========================
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    def restore(self, request, pk=None):
        product = self.get_object()

        if product.deleted_at is None:
            raise ValidationError("This product is not deleted.")

        product.restore()
        product.save()

        log_action(
            user=request.user,
            action="restore",
            instance=product,
            source="api",
        )

        return Response(
            {"detail": "Product restored successfully."},
            status=status.HTTP_200_OK,
        )

    # ==========================
    # Hard Delete (Admin only)
    # ==========================
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminUser],
        url_path="hard-delete",
    )
    def hard_delete(self, request, pk=None):
        product = self.get_object()

        if product.deleted_at is None:
            raise ValidationError(
                "Cannot hard delete an active product. Soft delete it first."
            )

        product.hard_delete()

        log_action(
            user=request.user,
            action="hard_delete",
            instance=product,
            source="api",
        )

        return Response(
            {"detail": f"Product (ID: {pk}) permanently deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )
