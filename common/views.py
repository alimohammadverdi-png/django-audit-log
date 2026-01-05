from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
)
from rest_framework_simplejwt.authentication import JWTAuthentication


class OwnedModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet with:
    - Ownership-based access control
    - Audit fields auto-fill
    - Soft delete as default destroy
    - ✅ NO custom actions (safe for inheritance)
    """

    # -------------------------
    # Authentication
    # -------------------------
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]

    # -------------------------
    # Permissions
    # -------------------------
    permission_classes = [IsAuthenticated]

    # Optional per-action permissions
    permission_classes_by_action = {}

    def get_permissions(self):
        perms = self.permission_classes_by_action.get(
            self.action,
            self.permission_classes,
        )
        return [permission() for permission in perms]

    # -------------------------
    # Queryset ownership
    # -------------------------
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return qs

        return qs.filter(owner=user)

    # -------------------------
    # Audit fields
    # -------------------------
    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    # -------------------------
    # Soft Delete (default DELETE)
    # -------------------------
    def perform_destroy(self, instance):
        instance.delete()
