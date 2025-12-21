from rest_framework import viewsets, status, permissions
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .models import User
from .serializers import (
    UserSerializer, UserListSerializer, UserCreateSerializer,
    LoginSerializer, RoleSerializer, ChangePasswordSerializer
)
from .permissions import RolePermissions
from .security import AccountLockoutManager, sanitize_input
from core.audit import AuditLogger
import logging

logger = logging.getLogger(__name__)


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
        
        # Sanitize input
        validated_data = serializer.validated_data
        if 'email' in validated_data:
            validated_data['email'] = sanitize_input(validated_data['email'])
        if 'username' in validated_data:
            validated_data['username'] = sanitize_input(validated_data['username'])
        
        # Create user
        new_user = serializer.save()
        
        # Log audit event
        try:
            AuditLogger.log_action(
                action_type='create',
                user=user,
                resource=new_user,
                description=f'Created user account: {new_user.username} ({new_user.email})',
                changes={'role': new_user.role},
                request=self.request,
            )
        except Exception as e:
            logger.error(f'Failed to log user creation audit: {e}')
    
    def perform_update(self, serializer):
        """Check permissions before update"""
        user = self.request.user
        target_user = self.get_object()
        
        # Track changes for audit log
        changes = {}
        old_role = target_user.role
        
        # Sanitize input
        validated_data = serializer.validated_data
        if 'email' in validated_data:
            validated_data['email'] = sanitize_input(validated_data['email'])
        if 'username' in validated_data:
            validated_data['username'] = sanitize_input(validated_data['username'])
        if 'full_name' in validated_data:
            validated_data['full_name'] = sanitize_input(validated_data.get('full_name'))
        
        # SuperAdmin and Admin can update any user
        if user.has_full_access():
            # Track role change
            if 'role' in validated_data and validated_data['role'] != old_role:
                changes['role'] = {'before': old_role, 'after': validated_data['role']}
            
            updated_user = serializer.save()
            
            # Log audit event
            try:
                AuditLogger.log_action(
                    action_type='update',
                    user=user,
                    resource=updated_user,
                    description=f'Updated user account: {updated_user.username}',
                    changes=changes if changes else None,
                    request=self.request,
                )
                
                # Log role change separately if occurred
                if changes.get('role'):
                    AuditLogger.log_action(
                        action_type='role_change',
                        user=user,
                        resource=updated_user,
                        description=f'Changed role from {old_role} to {updated_user.role} for user {updated_user.username}',
                        changes=changes['role'],
                        severity='critical',
                        request=self.request,
                    )
            except Exception as e:
                logger.error(f'Failed to log user update audit: {e}')
            
            return
        
        # Users can update their own profile (except role)
        if user.id == target_user.id:
            # Don't allow users to change their own role
            if 'role' in validated_data:
                validated_data.pop('role')
            
            updated_user = serializer.save()
            
            # Log audit event for self-update
            try:
                AuditLogger.log_action(
                    action_type='update',
                    user=user,
                    resource=updated_user,
                    description=f'Updated own profile',
                    request=self.request,
                )
            except Exception as e:
                logger.error(f'Failed to log user self-update audit: {e}')
            
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
        
        # Store user info before deletion for audit log
        deleted_username = instance.username
        deleted_email = instance.email
        deleted_role = instance.role
        
        instance.delete()
        
        # Log audit event
        try:
            AuditLogger.log_action(
                action_type='delete',
                user=user,
                resource_type='User',
                resource_name=f'{deleted_username} ({deleted_email})',
                description=f'Deleted user account: {deleted_username} (Role: {deleted_role})',
                changes={'deleted_user': deleted_username, 'deleted_role': deleted_role},
                severity='critical',
                request=self.request,
            )
        except Exception as e:
            logger.error(f'Failed to log user deletion audit: {e}')
    
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
        
        Requires old password for security. Logs audit event.
        """
        target_user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Check permissions
            if request.user.id != target_user.id and not request.user.has_full_access():
                raise PermissionDenied("You do not have permission to change this user's password.")
            
            # Change password
            target_user.set_password(serializer.validated_data['new_password'])
            target_user.save()
            
            # Log audit event
            try:
                AuditLogger.log_action(
                    action_type='password_change',
                    user=request.user,
                    resource=target_user if request.user.id == target_user.id else None,
                    resource_type='User' if request.user.id != target_user.id else None,
                    resource_name=target_user.username if request.user.id != target_user.id else None,
                    description=f'Password changed for user: {target_user.username}' if request.user.id != target_user.id else 'Changed own password',
                    severity='high',
                    request=request,
                )
            except Exception as e:
                logger.error(f'Failed to log password change audit: {e}')
            
            return Response({'status': 'password changed'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, id=None):
        """
        POST /api/users/{id}/change_role/
        Change user role (SuperAdmin/Admin only)
        
        Logs critical audit event for role changes.
        """
        target_user = self.get_object()
        
        # Only SuperAdmin and Admin can change roles
        if not request.user.has_full_access():
            raise PermissionDenied("You do not have permission to change user roles.")
        
        # Don't allow changing your own role
        if request.user.id == target_user.id:
            raise PermissionDenied("You cannot change your own role.")
        
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            old_role = target_user.role
            new_role = serializer.validated_data['role']
            
            # Don't allow changing to/from SuperAdmin unless current user is SuperAdmin
            if new_role == 'SuperAdmin' and not request.user.is_superadmin():
                raise PermissionDenied("Only SuperAdmin can assign SuperAdmin role.")
            
            if old_role == 'SuperAdmin' and not request.user.is_superadmin():
                raise PermissionDenied("Only SuperAdmin can change SuperAdmin role.")
            
            target_user.role = new_role
            target_user.save()
            
            # Log critical audit event
            try:
                AuditLogger.log_action(
                    action_type='role_change',
                    user=request.user,
                    resource=target_user,
                    description=f'Changed role from {old_role} to {new_role} for user {target_user.username}',
                    changes={'role': {'before': old_role, 'after': new_role}},
                    severity='critical',
                    request=request,
                )
            except Exception as e:
                logger.error(f'Failed to log role change audit: {e}')
            
            return Response({
                'status': 'role changed',
                'user_id': str(target_user.id),
                'new_role': new_role,
                'old_role': old_role,
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@never_cache
def login_view(request):
    """
    POST /api/auth/login/
    Authenticate user and return JWT token.
    
    Includes account lockout protection and audit logging.
    Prevents user enumeration by using consistent error messages.
    """
    # Sanitize input
    username = sanitize_input(request.data.get('username', ''))
    password = request.data.get('password', '')
    
    if not username or not password:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check for account lockout (by username or email)
    if AccountLockoutManager.is_locked(username):
        remaining_time = AccountLockoutManager.get_remaining_lockout_time(username)
        logger.warning(f'Login attempt for locked account: {username}')
        return Response({
            'error': 'Account temporarily locked due to multiple failed login attempts. Please try again later.',
            'lockout_seconds': remaining_time
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Check IP-based lockout as well
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    if AccountLockoutManager.is_locked(client_ip):
        remaining_time = AccountLockoutManager.get_remaining_lockout_time(client_ip)
        return Response({
            'error': 'Too many failed login attempts from this IP. Please try again later.',
            'lockout_seconds': remaining_time
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)  # Using 429 as Django doesn't have 423
    
    # Attempt authentication
    serializer = LoginSerializer(data={'username': username, 'password': password})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Clear any failed attempts
        AccountLockoutManager.clear_failed_attempts(username)
        AccountLockoutManager.clear_failed_attempts(user.email)
        AccountLockoutManager.clear_failed_attempts(client_ip)
        
        # Update last_seen
        user.update_last_seen()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Log successful login
        try:
            AuditLogger.log_authentication(
                action='login',
                user=user,
                success=True,
                request=request,
            )
        except Exception as e:
            logger.error(f'Failed to log login audit: {e}')
        
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
    
    # Authentication failed - record attempt (prevent user enumeration)
    # Don't reveal whether username exists or password is wrong
    is_locked_username, remaining_username = AccountLockoutManager.record_failed_attempt(username)
    is_locked_ip, remaining_ip = AccountLockoutManager.record_failed_attempt(client_ip)
    
    # Log failed login attempt
    try:
        # Try to get user for audit log (but don't reveal if it exists)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                user = None
        
        if user:
            AuditLogger.log_authentication(
                action='login',
                user=user,
                success=False,
                error_message='Invalid password',
                request=request,
            )
        else:
            # Log as unknown user to prevent enumeration
            AuditLogger.log_action(
                action_type='login',
                resource_type='User',
                resource_name='unknown',
                description=f'Failed login attempt for username: {username}',
                success=False,
                error_message='Invalid credentials',
                ip_address=client_ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
    except Exception as e:
        logger.error(f'Failed to log failed login audit: {e}')
    
    # Return generic error (prevent user enumeration)
    if is_locked_username or is_locked_ip:
        return Response({
            'error': 'Account temporarily locked due to multiple failed login attempts. Please try again later.',
            'lockout_seconds': max(remaining_username, remaining_ip)
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)  # Using 429 as Django doesn't have 423
    
    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@never_cache
def logout_view(request):
    """
    POST /api/auth/logout/
    Invalidate JWT token (blacklist refresh token)
    
    Logs logout action for audit trail.
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Log logout action
        try:
            AuditLogger.log_authentication(
                action='logout',
                user=request.user,
                success=True,
                request=request,
            )
        except Exception as e:
            logger.error(f'Failed to log logout audit: {e}')
        
        # Also logout session if exists
        logout(request)
        
        return Response({
            'status': 'success',
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Logout error: {e}')
        return Response({
            'status': 'error',
            'message': 'Failed to logout'
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
