"""
Accounts app URL configuration
"""
from django.urls import path
from .views import RegisterView, ProfileView, ProtectedTestView
from accounts.views import RBACPermissionTestView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', ProfileView.as_view(), name='me'),
    path('protected-test/', ProtectedTestView.as_view(), name='protected-test'),
]

urlpatterns = [
    path(
        'rbac-test/',
        RBACPermissionTestView.as_view(),
        name='rbac-test',
    ),
]