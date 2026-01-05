from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permissions.drf_permissions import HasRolePermission

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    
class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ProtectedTestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": f"Hello {request.user.username}, you are authenticated ✅"
        })
class RBACPermissionTestView(APIView):
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_permission = 'products.add_product'

    def get(self, request):
        return Response({
            'message': 'RBAC permission granted ✅',
            'role': request.user.role,
        })
                