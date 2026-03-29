from rest_framework import viewsets, status, permissions
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.conf import settings

from .models import User
from .serializers import (
    UserSerializer, UserListSerializer, UserCreateSerializer,
    LoginSerializer, RoleSerializer, ChangePasswordSerializer
)
from .permissions import RolePermissions
from .security import AccountLockoutManager, sanitize_input
from .sidebar_config import filter_sidebar_items
from core.audit import AuditLogger
from django.core.cache import cache
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

        if user.is_developer():
            return queryset

        if user.is_manager():
            q = queryset.filter(role='Employee')
            if user.organization_name:
                q = q.filter(organization_name=user.organization_name)
            return q

        return queryset.filter(id=user.id)
    
    def perform_create(self, serializer):
        """Check permissions before creating user"""
        user = self.request.user

        if user.is_employee():
            raise PermissionDenied("You do not have permission to create users.")
        if not (user.is_developer() or user.is_manager()):
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
        
        if user.is_developer():
            # Track role change
            if 'role' in validated_data and validated_data['role'] != old_role:
                changes['role'] = {'before': old_role, 'after': validated_data['role']}

            updated_user = serializer.save()

            try:
                AuditLogger.log_action(
                    action_type='update',
                    user=user,
                    resource=updated_user,
                    description=f'Updated user account: {updated_user.username}',
                    changes=changes if changes else None,
                    request=self.request,
                )

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

        if user.is_manager() and target_user.role == 'Employee' and user.id != target_user.id:
            if 'role' in validated_data and validated_data.get('role') != 'Employee':
                raise PermissionDenied("Managers can only manage Employee accounts.")
            validated_data['role'] = 'Employee'

            updated_user = serializer.save()
            try:
                AuditLogger.log_action(
                    action_type='update',
                    user=user,
                    resource=updated_user,
                    description=f'Updated user account: {updated_user.username}',
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

        if user.is_employee():
            raise PermissionDenied("You do not have permission to delete users.")

        if user.is_manager():
            if instance.role != 'Employee':
                raise PermissionDenied("You can only delete Employee accounts.")
        elif not user.is_developer():
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
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        GET /api/users/me/ - Get current user's profile
        PUT/PATCH /api/users/me/ - Update current user's profile
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        else:
            # PUT or PATCH - update profile
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                # Track changes for audit log
                changes = {}
                old_data = {
                    'email': request.user.email,
                    'full_name': request.user.full_name,
                    'phone_number': request.user.phone_number,
                }
                
                # Don't allow users to change their own role, is_active, is_staff, is_superuser
                protected_fields = ['role', 'is_active', 'is_staff', 'is_superuser']
                for field in protected_fields:
                    if field in serializer.validated_data:
                        serializer.validated_data.pop(field)
                
                # Save changes
                serializer.save()
                
                # Track changes for audit
                new_data = {
                    'email': request.user.email,
                    'full_name': request.user.full_name,
                    'phone_number': request.user.phone_number,
                }
                for key, old_value in old_data.items():
                    if new_data[key] != old_value:
                        changes[key] = {'before': old_value, 'after': new_data[key]}
                
                # Log audit event if changes were made
                if changes:
                    try:
                        AuditLogger.log_action(
                            action_type='update',
                            user=request.user,
                            resource=request.user,
                            description='Updated own profile',
                            changes=changes,
                            request=request,
                        )
                    except Exception as e:
                        logger.error(f'Failed to log profile update audit: {e}')
                
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """
        PUT/PATCH /api/users/update_me/
        Update current user's profile (alias for me endpoint)
        """
        return self.me(request)
    
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
    
    @action(detail=False, methods=['post'])
    def change_password_me(self, request):
        """
        POST /api/users/change_password_me/
        Change current user's password
        
        Requires old password for security. Logs audit event.
        """
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Change password
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            # Log audit event
            try:
                AuditLogger.log_action(
                    action_type='password_change',
                    user=request.user,
                    resource=request.user,
                    description='Changed own password',
                    severity='high',
                    request=request,
                )
            except Exception as e:
                logger.error(f'Failed to log password change audit: {e}')
            
            return Response({'status': 'password changed'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def activity_logs(self, request):
        """
        GET /api/users/activity_logs/
        Get current user's activity logs from audit system
        """
        from core.models import AuditLog
        from django.core.paginator import Paginator
        
        # Get user's activity logs
        logs = AuditLog.objects.filter(user=request.user).order_by('-timestamp')
        
        # Pagination
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        paginator = Paginator(logs, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize logs
        log_data = []
        for log in page_obj:
            log_data.append({
                'id': str(log.id),
                'action_type': log.action_type,
                'description': log.description,
                'timestamp': log.timestamp.isoformat(),
                'severity': log.severity,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'success': log.success,
            })
        
        return Response({
            'results': log_data,
            'count': paginator.count,
            'page': page_obj.number,
            'pages': paginator.num_pages,
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, id=None):
        """
        POST /api/users/{id}/change_role/
        Change user role (Developer only).
        """
        target_user = self.get_object()

        if not request.user.is_developer():
            raise PermissionDenied("Only a Developer can change user roles.")

        # Don't allow changing your own role
        if request.user.id == target_user.id:
            raise PermissionDenied("You cannot change your own role.")

        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            old_role = target_user.role
            new_role = serializer.validated_data['role']

            # Invalidate sidebar items cache for the user whose role changed
            cache_key = f'sidebar_items_{target_user.id}_{old_role}'
            cache.delete(cache_key)
            # Also delete any cache with new role (in case it exists)
            cache_key_new = f'sidebar_items_{target_user.id}_{new_role}'
            cache.delete(cache_key_new)
            
            target_user.role = new_role
            if new_role == 'Developer':
                target_user.is_superuser = True
                target_user.is_staff = True
            else:
                target_user.is_superuser = False
                target_user.is_staff = new_role == 'Manager'
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
    # Sanitize input and normalize username to lowercase
    username_raw = request.data.get('username', '')
    username = sanitize_input(username_raw).lower() if username_raw else ''
    password = request.data.get('password', '')
    
    logger.info(f'Login attempt - raw: "{username_raw}", normalized: "{username}", has_password: {bool(password)}')
    
    if not username or not password:
        logger.warning(f'Login attempt with missing credentials: username={bool(username)}, password={bool(password)}')
        return Response({
            'error': 'Please enter your username or email and password.'
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
    
    # Use serializer error message if available, otherwise generic message
    # Extract error from serializer.errors (non_field_errors or first field error)
    serializer_errors = serializer.errors if hasattr(serializer, 'errors') else {}
    error_message = 'Invalid credentials'
    
    if serializer_errors:
        # Check for non_field_errors first
        if 'non_field_errors' in serializer_errors:
            non_field_errors = serializer_errors['non_field_errors']
            if isinstance(non_field_errors, list) and len(non_field_errors) > 0:
                error_message = non_field_errors[0]
            elif isinstance(non_field_errors, str):
                error_message = non_field_errors
        else:
            # Get first field error
            for field, errors in serializer_errors.items():
                if isinstance(errors, list) and len(errors) > 0:
                    error_message = errors[0]
                    break
                elif isinstance(errors, str):
                    error_message = errors
                    break
    
    return Response({
        'error': error_message
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
@never_cache
def signup_view(request):
    """
    POST /api/auth/signup/
    Public endpoint to create a new user account.
    
    Allows unauthenticated users to register. New users are created with Employee role by default.
    """
    from .serializers import UserCreateSerializer

    serializer = UserCreateSerializer(data=request.data)

    if serializer.is_valid():
        serializer.validated_data['role'] = 'Employee'

        # Sanitize input
        if 'email' in serializer.validated_data:
            serializer.validated_data['email'] = sanitize_input(serializer.validated_data['email'])
        if 'username' in serializer.validated_data:
            serializer.validated_data['username'] = sanitize_input(serializer.validated_data['username'])

        user = serializer.save()
        
        # Log audit event (no user for unauthenticated signups)
        try:
            AuditLogger.log_action(
                action_type='create',
                resource=user,
                description=f'New user account created via signup: {user.username} ({user.email})',
                changes={'role': user.role},
                request=request,
            )
        except Exception as e:
            logger.error(f'Failed to log signup audit: {e}')
        
        # Generate JWT tokens for auto-login
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'message': 'Account created successfully',
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
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
def sessions_view(request):
    """
    GET /api/auth/sessions/
    Get current user's active sessions (simplified - returns current session info)
    
    Note: JWT tokens are stateless. This returns information about the current session
    based on the token. For full session management, consider implementing token storage.
    """
    from rest_framework_simplejwt.tokens import UntypedToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    import jwt
    from django.conf import settings
    
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    
    sessions = []
    if token:
        try:
            # Decode token to get info
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'], verify=False)
            sessions.append({
                'id': 'current',
                'device': request.META.get('HTTP_USER_AGENT', 'Unknown')[:100],
                'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
                'last_activity': timezone.now().isoformat(),
                'current': True,
            })
        except (InvalidToken, TokenError, jwt.DecodeError):
            pass
    
    return Response({
        'sessions': sessions,
        'count': len(sessions),
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@never_cache
def logout_all_view(request):
    """
    POST /api/auth/logout-all/
    Logout from all sessions (blacklist all refresh tokens for user)
    
    Note: This is a simplified implementation. For production, you may want to
    maintain a token whitelist/blacklist in the database.
    """
    try:
        # Log action
        try:
            AuditLogger.log_action(
                action_type='logout',
                user=request.user,
                resource=request.user,
                description='Logged out from all sessions',
                severity='medium',
                request=request,
            )
        except Exception as e:
            logger.error(f'Failed to log logout-all audit: {e}')
        
        # In a real implementation, you would:
        # 1. Store tokens in database with user_id
        # 2. Mark all tokens for this user as invalid
        # 3. Or use a token blacklist
        
        # For now, we'll just log the action
        # The user will need to change password to invalidate all tokens
        
        return Response({
            'status': 'success',
            'message': 'All sessions logged out. Please change your password to fully invalidate all tokens.'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Logout-all error: {e}')
        return Response({
            'status': 'error',
            'message': 'Failed to logout all sessions'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def roles_view(request):
    """
    GET /api/roles/
    Roles available for assignment in the UI (filtered by caller).
    """
    user = request.user
    if user.is_employee():
        raise PermissionDenied("You do not have permission to view roles.")

    if user.is_developer():
        roles = [
            {'value': 'Developer', 'label': 'Developer', 'description': 'Full system access'},
            {'value': 'Manager', 'label': 'Manager', 'description': 'Manage team and content; no system settings'},
            {'value': 'Employee', 'label': 'Employee', 'description': 'Screens, playlists, and media only'},
        ]
    else:
        roles = [
            {'value': 'Employee', 'label': 'Employee', 'description': 'Screens, playlists, and media only'},
        ]

    return Response({'roles': roles}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_role(request):
    """
    POST /api/roles/
    Create/Manage role (Developer only)
    Note: Roles are predefined, this endpoint is for future extensibility
    """
    if not request.user.is_developer():
        raise PermissionDenied("Only a Developer can manage roles.")
    
    return Response({
        'status': 'error',
        'message': 'Roles are predefined and cannot be created. Use /api/users/{id}/change_role/ to assign roles.'
    }, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationEmail(APIView):
    """
    POST /api/send-verification-email/
    Send email verification code to the authenticated user's email address
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Check if email is already verified
        if user.is_email_verified:
            return Response({
                'status': 'error',
                'message': 'Email is already verified.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has an email address
        if not user.email:
            return Response({
                'status': 'error',
                'message': 'No email address associated with this account.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate verification code
            code = user.generate_verification_code()
            
            # Send email
            subject = 'PixelCast Signage Email Verification Code'
            message = f'''
Hello {user.full_name or user.username},

Your email verification code is: {code}

This code will expire in 10 minutes.

If you did not request this code, please ignore this email.

Best regards,
PixelCast Signage Team
'''
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            # Log audit event
            try:
                AuditLogger.log_action(
                    action_type='email_verification_sent',
                    user=user,
                    resource=user,
                    description=f'Email verification code sent to {user.email}',
                    request=request,
                )
            except Exception as e:
                logger.error(f'Failed to log email verification sent audit: {e}')
            
            return Response({
                'status': 'success',
                'message': 'Verification code has been sent to your email address.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Failed to send verification email: {e}')
            return Response({
                'status': 'error',
                'message': 'Failed to send verification email. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmail(APIView):
    """
    POST /api/verify-email/
    Verify email address using the verification code
    Expected payload: {'code': '123456'}
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        code = request.data.get('code', '').strip()
        
        # Validate code is provided
        if not code:
            return Response({
                'status': 'error',
                'message': 'Verification code is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email is already verified
        if user.is_email_verified:
            return Response({
                'status': 'error',
                'message': 'Email is already verified.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has a verification code
        if not user.verification_code:
            return Response({
                'status': 'error',
                'message': 'No verification code found. Please request a new code.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if code has expired
        if user.verification_code_expiry and user.verification_code_expiry < timezone.now():
            # Clear expired code
            user.verification_code = None
            user.verification_code_expiry = None
            user.save(update_fields=['verification_code', 'verification_code_expiry'])
            
            return Response({
                'status': 'error',
                'message': 'Verification code has expired. Please request a new code.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify code matches
        if user.verification_code != code:
            # Log failed verification attempt
            try:
                AuditLogger.log_action(
                    action_type='email_verification_failed',
                    user=user,
                    resource=user,
                    description='Failed email verification attempt with invalid code',
                    request=request,
                )
            except Exception as e:
                logger.error(f'Failed to log email verification failed audit: {e}')
            
            return Response({
                'status': 'error',
                'message': 'Invalid verification code. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Code is valid - mark email as verified and clear code
        user.is_email_verified = True
        user.verification_code = None
        user.verification_code_expiry = None
        user.save(update_fields=['is_email_verified', 'verification_code', 'verification_code_expiry'])
        
        # Log successful verification
        try:
            AuditLogger.log_action(
                action_type='email_verified',
                user=user,
                resource=user,
                description=f'Email address {user.email} verified successfully',
                request=request,
            )
        except Exception as e:
            logger.error(f'Failed to log email verification audit: {e}')
        
        return Response({
            'status': 'success',
            'message': 'Email verified successfully!'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sidebar_items_view(request):
    """
    GET /api/sidebar-items/
    Get sidebar items for the authenticated user based on their role and permissions.
    Results are cached per user to improve performance.
    
    Returns:
        {
            'status': 'success',
            'items': [
                {
                    'id': 'dashboard',
                    'title': 'Dashboard',
                    'icon': 'HomeIcon',
                    'path': '/dashboard',
                    'badge': null,
                    'children': null
                },
                ...
            ]
        }
    """
    user = request.user
    
    # Cache key based on user ID and role (cache invalidates when role changes)
    cache_key = f'sidebar_items_{user.id}_{user.role}'
    
    # Try to get from cache
    cached_items = cache.get(cache_key)
    if cached_items is not None:
        return Response({
            'status': 'success',
            'items': cached_items
        }, status=status.HTTP_200_OK)
    
    # Filter sidebar items based on user permissions
    filtered_items = filter_sidebar_items(user)
    
    # Cache for 5 minutes (300 seconds)
    cache.set(cache_key, filtered_items, 300)
    
    return Response({
        'status': 'success',
        'items': filtered_items
    }, status=status.HTTP_200_OK)
