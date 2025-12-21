"""
Views for backup management and audit log access.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.utils import timezone
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from core.models import AuditLog, SystemBackup
from core.backup import backup_manager
from core.serializers import AuditLogSerializer, SystemBackupSerializer
from core.audit import AuditLogger
import logging

logger = logging.getLogger(__name__)


class RoleBasedPermission(BasePermission):
    """DRF permission class for role-based access control."""
    
    def __init__(self, required_roles=None):
        self.required_roles = required_roles or []
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not self.required_roles:
            return True
        
        user_role = getattr(request.user, 'role', None)
        return user_role in self.required_roles
    
    def has_object_permission(self, request, view, obj):
        # For object-level permissions, check user role
        if not request.user.is_authenticated:
            return False
        
        if not self.required_roles:
            return True
        
        user_role = getattr(request.user, 'role', None)
        return user_role in self.required_roles


@extend_schema_view(
    list=extend_schema(
        summary='List audit logs',
        description='Retrieve a paginated list of audit logs. Filterable by action type, resource type, severity, success status, date range, and search query.',
        tags=['Core Infrastructure'],
        parameters=[
            OpenApiParameter(
                name='action_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by action type (create, update, delete, login, etc.)',
                required=False,
            ),
            OpenApiParameter(
                name='resource_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by resource type (Screen, Template, Content, etc.)',
                required=False,
            ),
            OpenApiParameter(
                name='severity',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by severity (low, medium, high, critical)',
                required=False,
                enum=['low', 'medium', 'high', 'critical'],
            ),
            OpenApiParameter(
                name='success',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by success status',
                required=False,
            ),
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter logs from this date (YYYY-MM-DD)',
                required=False,
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter logs until this date (YYYY-MM-DD)',
                required=False,
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in description, resource name, or username',
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary='Retrieve audit log',
        description='Retrieve detailed information about a specific audit log entry.',
        tags=['Core Infrastructure'],
    ),
)
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs.

    Permissions:
    - Viewers: Can view their own logs
    - Operators: Can view logs for assigned resources
    - Managers/Admins: Can view all logs
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    queryset = AuditLog.objects.all()

    def get_queryset(self):
        """Filter audit logs based on user permissions."""
        user = self.request.user
        queryset = AuditLog.objects.all()

        # Apply role-based filtering
        user_role = getattr(user, 'role', None)
        if user_role in ('SuperAdmin', 'Admin', 'Manager'):
            # Admins and Managers can see all logs
            pass
        elif user_role == 'Operator':
            # Operators see logs for their assigned resources (simplified: own logs)
            queryset = queryset.filter(user=user)
        else:
            # Viewers see only their own logs
            queryset = queryset.filter(user=user)

        # Apply filters from query params
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)

        resource_type = self.request.query_params.get('resource_type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)

        success = self.request.query_params.get('success')
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')

        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(resource_name__icontains=search) |
                Q(username__icontains=search)
            )

        return queryset.order_by('-timestamp')

    @extend_schema(
        summary='Get audit log summary',
        description='Get summary statistics for audit logs including counts by action type and severity.',
        tags=['Core Infrastructure'],
        responses={
            200: AuditLogSerializer(many=True),
        },
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for audit logs."""
        queryset = self.get_queryset()

        total_count = queryset.count()
        success_count = queryset.filter(success=True).count()
        failed_count = queryset.filter(success=False).count()

        action_type_counts = {}
        for action_type, _ in AuditLog.ACTION_TYPES:
            count = queryset.filter(action_type=action_type).count()
            if count > 0:
                action_type_counts[action_type] = count

        severity_counts = {}
        for severity, _ in AuditLog.SEVERITY_LEVELS:
            count = queryset.filter(severity=severity).count()
            if count > 0:
                severity_counts[severity] = count

        return Response({
            'total_count': total_count,
            'success_count': success_count,
            'failed_count': failed_count,
            'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
            'action_type_counts': action_type_counts,
            'severity_counts': severity_counts,
        })


@extend_schema_view(
    list=extend_schema(
        summary='List system backups',
        description='Retrieve a paginated list of system backups. Filterable by backup type and status.',
        tags=['Core Infrastructure'],
        parameters=[
            OpenApiParameter(
                name='backup_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by backup type',
                required=False,
                enum=['database', 'media', 'full', 'incremental'],
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by backup status',
                required=False,
                enum=['pending', 'in_progress', 'completed', 'failed', 'expired'],
            ),
        ],
    ),
    retrieve=extend_schema(
        summary='Retrieve backup details',
        description='Retrieve detailed information about a specific backup.',
        tags=['Core Infrastructure'],
    ),
    create=extend_schema(
        summary='Create backup record',
        description='Create a new backup record (typically created automatically when backup is triggered).',
        tags=['Core Infrastructure'],
    ),
    update=extend_schema(
        summary='Update backup',
        description='Update backup record (limited fields).',
        tags=['Core Infrastructure'],
        exclude=True,  # Usually backups shouldn't be manually updated
    ),
    partial_update=extend_schema(
        summary='Partially update backup',
        description='Partially update backup record.',
        tags=['Core Infrastructure'],
        exclude=True,
    ),
    destroy=extend_schema(
        summary='Delete backup',
        description='Delete a backup record and optionally its file.',
        tags=['Core Infrastructure'],
    ),
)
class SystemBackupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing system backups.

    Permissions:
    - Only Managers and Admins can create/delete backups
    - All authenticated users can view backups
    """
    serializer_class = SystemBackupSerializer
    permission_classes = [IsAuthenticated]
    queryset = SystemBackup.objects.all()

    def get_queryset(self):
        """Filter backups."""
        queryset = SystemBackup.objects.all()

        backup_type = self.request.query_params.get('backup_type')
        if backup_type:
            queryset = queryset.filter(backup_type=backup_type)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-started_at')

    def get_permissions(self):
        """Apply stricter permissions for create/delete."""
        if self.action in ('create', 'destroy', 'trigger', 'cleanup'):
            return [IsAuthenticated(), RoleBasedPermission(required_roles=['SuperAdmin', 'Admin', 'Manager'])]
        return super().get_permissions()

    @extend_schema(
        summary='Trigger backup',
        description='Manually trigger a system backup. Requires Manager, Admin, or SuperAdmin role.',
        tags=['Core Infrastructure'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'backup_type': {
                        'type': 'string',
                        'enum': ['database', 'media', 'full'],
                        'description': 'Type of backup to create',
                        'default': 'database',
                    },
                    'compression': {
                        'type': 'boolean',
                        'description': 'Enable compression (default: true)',
                        'default': True,
                    },
                    'include_media': {
                        'type': 'boolean',
                        'description': 'Include media files (only for database type, default: false)',
                        'default': False,
                    },
                },
                'required': ['backup_type'],
                'example': {
                    'backup_type': 'database',
                    'compression': True,
                    'include_media': False,
                },
            }
        },
        responses={
            201: SystemBackupSerializer,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Database Backup Request',
                value={
                    'backup_type': 'database',
                    'compression': True,
                },
                request_only=True,
            ),
            OpenApiExample(
                'Media Backup Request',
                value={
                    'backup_type': 'media',
                    'compression': True,
                },
                request_only=True,
            ),
            OpenApiExample(
                'Full Backup Request',
                value={
                    'backup_type': 'full',
                    'compression': True,
                },
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'])
    def trigger(self, request):
        """
        Manually trigger a backup.

        Request body:
        {
            "backup_type": "database" | "media" | "full",
            "compression": true,
            "include_media": false (only for database type)
        }
        """
        backup_type = request.data.get('backup_type', 'database')
        compression = request.data.get('compression', True)

        try:
            if backup_type == 'database':
                backup = backup_manager.backup_database(
                    include_media=request.data.get('include_media', False),
                    compression=compression,
                    user=request.user
                )
            elif backup_type == 'media':
                backup = backup_manager.backup_media(
                    compression=compression,
                    user=request.user
                )
            elif backup_type == 'full':
                backup = backup_manager.backup_full(
                    compression=compression,
                    user=request.user
                )
            else:
                return Response(
                    {'error': f'Invalid backup_type: {backup_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(backup)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Backup trigger failed: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary='Verify backup integrity',
        description='Verify the integrity of a backup file by checking its checksum.',
        tags=['Core Infrastructure'],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'is_valid': {'type': 'boolean', 'description': 'Whether backup file is valid'},
                    'checksum_match': {'type': 'boolean', 'description': 'Whether checksum matches'},
                },
            },
            404: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify backup integrity."""
        backup = self.get_object()

        is_valid = backup_manager.verify_backup(backup)

        # Log verification
        AuditLogger.log_action(
            action_type='read',
            user=request.user,
            resource=backup,
            description=f"Backup verification: {'passed' if is_valid else 'failed'}",
            success=is_valid,
            request=request,
        )

        return Response({
            'is_valid': is_valid,
            'checksum_match': is_valid,
        })

    @extend_schema(
        summary='Cleanup expired backups',
        description='Delete expired backups based on retention policy. Requires Manager, Admin, or SuperAdmin role.',
        tags=['Core Infrastructure'],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'deleted_count': {'type': 'integer', 'description': 'Number of backups deleted'},
                    'message': {'type': 'string', 'description': 'Success message'},
                },
            },
            403: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=False, methods=['post'])
    def cleanup(self, request):
        """Cleanup expired backups."""
        user_role = getattr(request.user, 'role', None)
        if user_role not in ('SuperAdmin', 'Admin', 'Manager'):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        deleted_count = backup_manager.cleanup_expired_backups()

        # Log cleanup
        AuditLogger.log_action(
            action_type='delete',
            user=request.user,
            resource_type='System',
            description=f"Cleaned up {deleted_count} expired backups",
            request=request,
        )

        return Response({
            'deleted_count': deleted_count,
            'message': f'Cleaned up {deleted_count} expired backups'
        })
