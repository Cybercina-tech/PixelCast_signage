from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from .models import User
from .serializers import (
    UserSerializer, UserListSerializer, UserCreateSerializer,
    LoginSerializer, RoleSerializer, ChangePasswordSerializer
)
from .permissions import RolePermissions


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    Provides CRUD operations with role-based permissions.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # SuperAdmin and Admin can see all users
        if user.has_full_access():
            return queryset
        
        # Manager, Operator, Viewer can see users in their organization
        if user.organization_name:
            return queryset.filter(organization_name=user.organization_name)
        
        # Otherwise, only see themselves
        return queryset.filter(id=user.id)
    
    def perform_create(self, serializer):
        """Check permissions before creating user"""
        user = self.request.user
        
        # Only SuperAdmin and Admin can create users
        if not user.has_full_access():
            raise PermissionDenied("You do not have permission to create users.")
        
        # Set created_by if not set
        serializer.save()
    
    def perform_update(self, serializer):
        """Check permissions before update"""
        user = self.request.user
        target_user = self.get_object()
        
        # SuperAdmin and Admin can update any user
        if user.has_full_access():
            serializer.save()
            return
        
        # Users can update their own profile (except role)
        if user.id == target_user.id:
            # Don't allow users to change their own role
            if 'role' in serializer.validated_data:
                serializer.validated_data.pop('role')
            serializer.save()
            return
        
        # Otherwise, no permission
        raise PermissionDenied("You do not have permission to update this user.")
    
    def perform_destroy(self, instance):
        """Check permissions before delete"""
        user = self.request.user
        
        # Only SuperAdmin and Admin can delete users
        if not user.has_full_access():
            raise PermissionDenied("You do not have permission to delete users.")
        
        # Don't allow deleting yourself
        if user.id == instance.id:
            raise PermissionDenied("You cannot delete your own account.")
        
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        GET /api/users/me/
        Get current user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """
        PUT/PATCH /api/users/update_me/
        Update current user's profile
        """
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            # Don't allow users to change their own role
            if 'role' in serializer.validated_data:
                serializer.validated_data.pop('role')
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, id=None):
        """
        POST /api/users/{id}/change_password/
        Change user password
        """
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Check permissions
            if request.user.id != user.id and not request.user.has_full_access():
                raise PermissionDenied("You do not have permission to change this user's password.")
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'password changed'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, id=None):
        """
        POST /api/users/{id}/change_role/
        Change user role (SuperAdmin/Admin only)
        """
        user = self.get_object()
        
        # Only SuperAdmin and Admin can change roles
        if not request.user.has_full_access():
            raise PermissionDenied("You do not have permission to change user roles.")
        
        # Don't allow changing your own role
        if request.user.id == user.id:
            raise PermissionDenied("You cannot change your own role.")
        
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            new_role = serializer.validated_data['role']
            user.role = new_role
            user.save()
            return Response({
                'status': 'role changed',
                'user_id': str(user.id),
                'new_role': new_role
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST /api/auth/login/
    Authenticate user and return JWT token
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Update last_seen
        user.update_last_seen()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'role_display': user.get_role_display(),
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST /api/auth/logout/
    Invalidate JWT token (blacklist refresh token)
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Also logout session if exists
        logout(request)
        
        return Response({
            'status': 'success',
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def roles_view(request):
    """
    GET /api/roles/
    Get available roles (SuperAdmin/Admin only)
    """
    # Only SuperAdmin and Admin can view roles
    if not request.user.has_full_access():
        raise PermissionDenied("You do not have permission to view roles.")
    
    roles = [
        {
            'value': 'SuperAdmin',
            'label': 'Super Admin',
            'description': 'Full system access with all permissions'
        },
        {
            'value': 'Admin',
            'label': 'Admin',
            'description': 'Administrative access to manage users and resources'
        },
        {
            'value': 'Operator',
            'label': 'Operator',
            'description': 'Can execute commands and manage resources'
        },
        {
            'value': 'Manager',
            'label': 'Manager',
            'description': 'Can manage own resources and view reports'
        },
        {
            'value': 'Viewer',
            'label': 'Viewer',
            'description': 'Read-only access to view resources'
        },
    ]
    
    return Response({
        'roles': roles
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_role(request):
    """
    POST /api/roles/
    Create/Manage role (SuperAdmin only)
    Note: Roles are predefined, this endpoint is for future extensibility
    """
    # Only SuperAdmin can manage roles
    if not request.user.is_superadmin():
        raise PermissionDenied("Only SuperAdmin can manage roles.")
    
    return Response({
        'status': 'error',
        'message': 'Roles are predefined and cannot be created. Use /api/users/{id}/change_role/ to assign roles.'
    }, status=status.HTTP_400_BAD_REQUEST)
