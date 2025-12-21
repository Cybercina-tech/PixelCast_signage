from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.utils import timezone
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .models import Template, Layer, Widget, Content, Schedule
from .serializers import (
    TemplateSerializer, TemplateListSerializer, LayerSerializer,
    WidgetSerializer, ContentSerializer, ScheduleSerializer,
    ScheduleListSerializer, TemplateActivationSerializer,
    ScheduleExecutionSerializer
)
from accounts.permissions import RolePermissions
from log.models import ContentDownloadLog


class TemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Template model.
    Provides CRUD operations with role-based permissions.
    """
    queryset = Template.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return TemplateListSerializer
        return TemplateSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # SuperAdmin and Admin can see all templates
        if user.has_full_access():
            return queryset
        
        # Manager, Operator, Viewer can see templates they created or in their organization
        if user.can_manage_own_resources():
            # Get users in same organization
            org_users = user.get_organization_users()
            return queryset.filter(
                Q(created_by=user) | Q(created_by__in=org_users)
            )
        
        # Viewer can only see their own templates
        return queryset.filter(created_by=user)
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Check permissions before update"""
        template = self.get_object()
        user = self.request.user
        
        # Check if user can edit this template
        if not RolePermissions.can_edit_resource(user, template):
            raise PermissionDenied("You do not have permission to edit this template")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Check permissions before delete"""
        user = self.request.user
        
        # Only SuperAdmin, Admin, or creator can delete
        if not (user.has_full_access() or instance.created_by == user):
            raise PermissionDenied("You do not have permission to delete this template")
        
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def activate_on_screen(self, request, id=None):
        """
        POST /api/templates/{id}/activate_on_screen/
        Activate this template on a specific screen.
        """
        template = self.get_object()
        serializer = TemplateActivationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Check permissions
        user = request.user
        if not RolePermissions.can_edit_resource(user, template):
            raise PermissionDenied("You do not have permission to activate this template")
        
        from signage.models import Screen
        try:
            screen = Screen.objects.get(id=serializer.validated_data['screen_id'])
        except Screen.DoesNotExist:
            return Response(
                {'error': 'Screen not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user can access the screen
        if not RolePermissions.can_view_resource(user, screen):
            raise PermissionDenied("You do not have permission to access this screen")
        
        sync_content = serializer.validated_data.get('sync_content', True)
        success = template.activate_on_screen(screen, sync_content=sync_content)
        
        if success:
            return Response({
                'status': 'success',
                'message': f'Template "{template.name}" activated on screen "{screen.name}"',
                'template_id': str(template.id),
                'screen_id': str(screen.id)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to activate template. Template may not be active.'
            }, status=status.HTTP_400_BAD_REQUEST)


class LayerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Layer model.
    Provides CRUD operations with role-based permissions.
    """
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by template permissions
        if user.has_full_access():
            return queryset
        
        # Get accessible templates
        if user.can_manage_own_resources():
            org_users = user.get_organization_users()
            accessible_templates = Template.objects.filter(
                Q(created_by=user) | Q(created_by__in=org_users)
            )
        else:
            accessible_templates = Template.objects.filter(created_by=user)
        
        return queryset.filter(template__in=accessible_templates)
    
    def perform_create(self, serializer):
        """Check permissions for template"""
        template = serializer.validated_data.get('template')
        user = self.request.user
        
        if not RolePermissions.can_edit_resource(user, template):
            raise PermissionDenied("You do not have permission to create layers for this template")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Check permissions before update"""
        layer = self.get_object()
        user = self.request.user
        
        if not RolePermissions.can_edit_resource(user, layer.template):
            raise PermissionDenied("You do not have permission to edit this layer")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Check permissions before delete"""
        user = self.request.user
        
        if not RolePermissions.can_edit_resource(user, instance.template):
            raise PermissionDenied("You do not have permission to delete this layer")
        
        instance.delete()


class WidgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Widget model.
    Provides CRUD operations with role-based permissions.
    """
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by layer permissions (which filter by template)
        if user.has_full_access():
            return queryset
        
        # Get accessible templates
        if user.can_manage_own_resources():
            org_users = user.get_organization_users()
            accessible_templates = Template.objects.filter(
                Q(created_by=user) | Q(created_by__in=org_users)
            )
        else:
            accessible_templates = Template.objects.filter(created_by=user)
        
        # Get layers for accessible templates
        from .models import Layer
        accessible_layers = Layer.objects.filter(template__in=accessible_templates)
        
        return queryset.filter(layer__in=accessible_layers)
    
    def perform_create(self, serializer):
        """Check permissions for layer"""
        layer = serializer.validated_data.get('layer')
        user = self.request.user
        
        if not RolePermissions.can_edit_resource(user, layer.template):
            raise PermissionDenied("You do not have permission to create widgets for this layer")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Check permissions before update"""
        widget = self.get_object()
        user = self.request.user
        
        if not RolePermissions.can_edit_resource(user, widget.layer.template):
            raise PermissionDenied("You do not have permission to edit this widget")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Check permissions before delete"""
        user = self.request.user
        
        if not RolePermissions.can_edit_resource(user, instance.layer.template):
            raise PermissionDenied("You do not have permission to delete this widget")
        
        instance.delete()


class ContentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Content model.
    Provides CRUD operations with role-based permissions.
    """
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by widget permissions (which filter by layer/template)
        if user.has_full_access():
            return queryset
        
        # Get accessible templates
        if user.can_manage_own_resources():
            org_users = user.get_organization_users()
            accessible_templates = Template.objects.filter(
                Q(created_by=user) | Q(created_by__in=org_users)
            )
        else:
            accessible_templates = Template.objects.filter(created_by=user)
        
        # Get widgets for accessible templates
        from .models import Layer, Widget
        accessible_layers = Layer.objects.filter(template__in=accessible_templates)
        accessible_widgets = Widget.objects.filter(layer__in=accessible_layers)
        
        return queryset.filter(widget__in=accessible_widgets)
    
    def perform_create(self, serializer):
        """Check permissions for widget"""
        widget = serializer.validated_data.get('widget')
        user = self.request.user
        
        if not RolePermissions.can_edit_resource(user, widget.layer.template):
            raise PermissionDenied("You do not have permission to create content for this widget")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Check permissions before update"""
        content = self.get_object()
        user = self.request.user
        
        if not RolePermissions.can_edit_resource(user, content.widget.layer.template):
            raise PermissionDenied("You do not have permission to edit this content")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Check permissions before delete"""
        user = self.request.user
        
        if not RolePermissions.can_edit_resource(user, instance.widget.layer.template):
            raise PermissionDenied("You do not have permission to delete this content")
        
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def download_to_screen(self, request, id=None):
        """
        POST /api/contents/{id}/download_to_screen/
        Download content to a specific screen.
        """
        content = self.get_object()
        screen_id = request.data.get('screen_id')
        
        if not screen_id:
            return Response(
                {'error': 'screen_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        user = request.user
        if not RolePermissions.can_edit_resource(user, content.widget.layer.template):
            raise PermissionDenied("You do not have permission to download this content")
        
        from signage.models import Screen
        try:
            screen = Screen.objects.get(id=screen_id)
        except Screen.DoesNotExist:
            return Response(
                {'error': 'Screen not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user can access the screen
        if not RolePermissions.can_view_resource(user, screen):
            raise PermissionDenied("You do not have permission to access this screen")
        
        try:
            success = content.download_to_screen(screen)
            if success:
                return Response({
                    'status': 'success',
                    'message': f'Content "{content.name}" downloaded to screen "{screen.name}"',
                    'content_id': str(content.id),
                    'screen_id': str(screen.id)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Download failed'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def retry_download(self, request, id=None):
        """
        POST /api/contents/{id}/retry_download/
        Retry downloading content to a screen.
        """
        content = self.get_object()
        screen_id = request.data.get('screen_id')
        max_retries = request.data.get('max_retries', 3)
        
        if not screen_id:
            return Response(
                {'error': 'screen_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        user = request.user
        if not RolePermissions.can_edit_resource(user, content.widget.layer.template):
            raise PermissionDenied("You do not have permission to retry download for this content")
        
        from signage.models import Screen
        try:
            screen = Screen.objects.get(id=screen_id)
        except Screen.DoesNotExist:
            return Response(
                {'error': 'Screen not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user can access the screen
        if not RolePermissions.can_view_resource(user, screen):
            raise PermissionDenied("You do not have permission to access this screen")
        
        try:
            success = content.retry_download(screen, max_retries=max_retries)
            if success:
                return Response({
                    'status': 'success',
                    'message': f'Content "{content.name}" retry download successful',
                    'content_id': str(content.id),
                    'screen_id': str(screen.id)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Retry download failed'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request, id=None):
        """
        POST /api/contents/{id}/upload/
        Upload a file for content.
        Requires multipart/form-data with 'file' field.
        """
        content = self.get_object()
        user = request.user
        
        # Check permissions
        if not RolePermissions.can_edit_resource(user, content.widget.layer.template):
            raise PermissionDenied("You do not have permission to upload content for this widget")
        
        # Check if file is provided
        if 'file' not in request.FILES:
            return Response(
                {'error': 'File is required. Use multipart/form-data with "file" field.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_obj = request.FILES['file']
        
        try:
            # Validate content before saving (comprehensive validation is done in storage.py)
            # Additional pre-save checks can be added here if needed
            
            # Save uploaded file (includes comprehensive validation)
            metadata = content.save_uploaded_file(file_obj, user)
            
            # Log upload operation
            from log.models import ContentDownloadLog
            ContentDownloadLog.objects.create(
                content=content,
                status='success',
                file_size=metadata.get('file_size'),
                downloaded_at=timezone.now()
            )
            
            return Response({
                'status': 'success',
                'message': f'File uploaded successfully for content "{content.name}"',
                'content_id': str(content.id),
                'file_url': content.file_url,
                'file_size': content.file_size,
                'file_hash': content.file_hash,
                'storage_path': content.storage_path
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Upload failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def download(self, request, id=None):
        """
        GET /api/contents/{id}/download/
        Get secure download URL for content file.
        Returns signed URL for S3 or media URL for local storage.
        """
        content = self.get_object()
        user = request.user
        
        # Check permissions
        if not RolePermissions.can_view_resource(user, content.widget.layer.template):
            raise PermissionDenied("You do not have permission to download this content")
        
        if not content.file_url and not content.storage_path:
            return Response(
                {'error': 'Content has no file to download'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Get expiration from query params (optional)
            expiration = request.query_params.get('expiration', None)
            expiration = int(expiration) if expiration else None
            
            # Get secure URL
            secure_url = content.get_secure_url(expiration)
            
            # Log download access
            from log.models import ContentDownloadLog
            ContentDownloadLog.objects.create(
                content=content,
                status='success',
                file_size=content.file_size,
                downloaded_at=timezone.now()
            )
            
            return Response({
                'status': 'success',
                'content_id': str(content.id),
                'download_url': secure_url,
                'expiration': expiration or getattr(settings, 'CONTENT_STORAGE', {}).get('SIGNED_URL_EXPIRATION', 3600),
                'file_size': content.file_size,
                'file_hash': content.file_hash,
                'hash_algorithm': content.hash_algorithm
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to generate download URL: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def verify_integrity(self, request, id=None):
        """
        POST /api/contents/{id}/verify_integrity/
        Verify content file integrity using hash.
        """
        content = self.get_object()
        user = request.user
        
        # Check permissions
        if not RolePermissions.can_view_resource(user, content.widget.layer.template):
            raise PermissionDenied("You do not have permission to verify this content")
        
        if not content.file_hash:
            return Response({
                'status': 'warning',
                'message': 'Content has no hash for integrity verification'
            }, status=status.HTTP_200_OK)
        
        try:
            is_valid, error = content.verify_integrity()
            
            if is_valid:
                return Response({
                    'status': 'success',
                    'message': 'Content integrity verified successfully',
                    'content_id': str(content.id),
                    'file_hash': content.file_hash,
                    'hash_algorithm': content.hash_algorithm
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': f'Content integrity check failed: {error}',
                    'content_id': str(content.id)
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Integrity verification failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Schedule model.
    Provides CRUD operations with role-based permissions and schedule execution.
    """
    queryset = Schedule.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ScheduleListSerializer
        return ScheduleSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # SuperAdmin and Admin can see all schedules
        if user.has_full_access():
            return queryset
        
        # Manager, Operator, Viewer can see schedules for templates they can access
        if user.can_manage_own_resources():
            org_users = user.get_organization_users()
            accessible_templates = Template.objects.filter(
                Q(created_by=user) | Q(created_by__in=org_users)
            )
        else:
            accessible_templates = Template.objects.filter(created_by=user)
        
        return queryset.filter(template__in=accessible_templates)
    
    def perform_create(self, serializer):
        """Check permissions for template"""
        template = serializer.validated_data.get('template')
        user = self.request.user
        
        # Only SuperAdmin, Admin, Operator, Manager can create schedules
        if not user.can_manage_own_resources():
            raise PermissionDenied("You do not have permission to create schedules")
        
        if not RolePermissions.can_edit_resource(user, template):
            raise PermissionDenied("You do not have permission to create schedules for this template")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Check permissions before update"""
        schedule = self.get_object()
        user = self.request.user
        
        # Only SuperAdmin, Admin, Operator, Manager can update schedules
        if not user.can_manage_own_resources():
            raise PermissionDenied("You do not have permission to update schedules")
        
        if not RolePermissions.can_edit_resource(user, schedule.template):
            raise PermissionDenied("You do not have permission to edit this schedule")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Check permissions before delete"""
        user = self.request.user
        
        # Only SuperAdmin, Admin, Operator, Manager can delete schedules
        if not user.can_manage_own_resources():
            raise PermissionDenied("You do not have permission to delete schedules")
        
        if not RolePermissions.can_edit_resource(user, instance.template):
            raise PermissionDenied("You do not have permission to delete this schedule")
        
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def execute(self, request, id=None):
        """
        POST /api/schedules/{id}/execute/
        Execute a schedule on its assigned screens.
        """
        schedule = self.get_object()
        serializer = ScheduleExecutionSerializer(data=request.data, instance=schedule)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Check permissions
        user = request.user
        if not user.can_execute_commands():
            raise PermissionDenied("You do not have permission to execute schedules")
        
        if not RolePermissions.can_edit_resource(user, schedule.template):
            raise PermissionDenied("You do not have permission to execute this schedule")
        
        force = serializer.validated_data.get('force', False)
        
        # Check if schedule should run
        if not force and not schedule.is_running_now:
            return Response({
                'status': 'error',
                'message': 'Schedule is not due to run. Use force=true to execute anyway.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Execute schedule
        result = schedule.execute_on_screens()
        
        return Response({
            'status': 'success',
            'message': f'Schedule "{schedule.name}" executed',
            'schedule_id': str(schedule.id),
            'execution_result': result
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def due_schedules(self, request):
        """
        GET /api/schedules/due_schedules/
        Get all schedules that are due to run now.
        """
        user = request.user
        
        # Get accessible schedules
        queryset = self.get_queryset()
        
        # Filter for schedules that are running now
        due_schedules = []
        for schedule in queryset:
            if schedule.is_running_now:
                due_schedules.append(schedule)
        
        serializer = self.get_serializer(due_schedules, many=True)
        return Response({
            'count': len(due_schedules),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def conflicting(self, request):
        """
        GET /api/schedules/conflicting/
        Get all schedule conflicts.
        """
        user = request.user
        
        if not user.has_full_access():
            raise PermissionDenied("Only administrators can view schedule conflicts")
        
        queryset = self.get_queryset().filter(is_active=True)
        conflicts = []
        
        schedules = list(queryset)
        for i, schedule1 in enumerate(schedules):
            for schedule2 in schedules[i+1:]:
                if schedule1.is_conflicting(schedule2):
                    conflicts.append({
                        'schedule1': {
                            'id': str(schedule1.id),
                            'name': schedule1.name,
                            'priority': schedule1.priority
                        },
                        'schedule2': {
                            'id': str(schedule2.id),
                            'name': schedule2.name,
                            'priority': schedule2.priority
                        },
                        'resolution': 'schedule1' if schedule1.priority >= schedule2.priority else 'schedule2'
                    })
        
        return Response({
            'count': len(conflicts),
            'conflicts': conflicts
        }, status=status.HTTP_200_OK)
