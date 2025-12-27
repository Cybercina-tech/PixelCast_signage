from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

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
    
    def create(self, request, *args, **kwargs):
        """Handle template creation with better error messages"""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            # Return detailed validation errors
            return Response({
                'status': 'error',
                'errors': e.detail,
                'message': 'Template creation failed. Please check the provided data.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating the template. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
            # Provide detailed response including screen status
            response_data = {
                'status': 'success',
                'message': f'Template "{template.name}" activated on screen "{screen.name}"',
                'template_id': str(template.id),
                'screen_id': str(screen.id),
                'screen_online': screen.is_online,
                'content_sync': sync_content,
            }
            
            # Add warning if screen is offline and content sync was requested
            if not screen.is_online and sync_content:
                response_data['warning'] = 'Screen is offline. Content will be synced when screen comes online.'
            
            return Response(response_data, status=status.HTTP_200_OK)
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
        """Filter queryset based on user permissions and template query parameter"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by template query parameter if provided
        template_id = self.request.query_params.get('template')
        if template_id:
            try:
                template = Template.objects.get(id=template_id)
                # Check if user has access to this template
                if user.has_full_access() or RolePermissions.can_view_resource(user, template):
                    return queryset.filter(template=template)
                else:
                    # User doesn't have access to this template
                    return queryset.none()
            except Template.DoesNotExist:
                # Template not found
                return queryset.none()
        
        # If no template filter, filter by template permissions
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
        """Filter queryset based on user permissions and layer query parameter"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by layer query parameter if provided
        layer_id = self.request.query_params.get('layer')
        if layer_id:
            try:
                layer = Layer.objects.get(id=layer_id)
                # Check if user has access to this layer's template
                if user.has_full_access() or RolePermissions.can_view_resource(user, layer.template):
                    return queryset.filter(layer=layer)
                else:
                    # User doesn't have access to this layer
                    return queryset.none()
            except Layer.DoesNotExist:
                # Layer not found
                return queryset.none()
        
        # If no layer filter, filter by layer permissions (which filter by template)
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
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def update(self, request, *args, **kwargs):
        """Handle content update with better error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except PermissionDenied:
            raise
        except serializers.ValidationError as e:
            logger.error(f"Validation error updating content: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'errors': e.detail,
                'message': 'Content update failed validation. Please check the provided data.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating content: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'message': f'Failed to update content: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
        
        if not widget:
            raise PermissionDenied("Widget is required to create content")
        
        try:
            if not widget.layer:
                raise PermissionDenied("Widget must have a layer assigned")
            
            if not widget.layer.template:
                raise PermissionDenied("Widget layer must have a template assigned")
            
            if not RolePermissions.can_edit_resource(user, widget.layer.template):
                raise PermissionDenied("You do not have permission to create content for this widget")
        except AttributeError as e:
            logger.error(f"Error accessing widget relationships during content creation: {str(e)}", exc_info=True)
            raise PermissionDenied("Error checking permissions. Widget may have invalid relationships.")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Check permissions before update"""
        content = self.get_object()
        user = self.request.user
        
        # Check if content has required relationships (handle potential None values)
        try:
            widget = content.widget
            if not widget:
                logger.error(f"Content {content.id} has no widget assigned")
                raise PermissionDenied("Content must have a widget assigned")
            
            layer = widget.layer
            if not layer:
                logger.error(f"Widget {widget.id} has no layer assigned")
                raise PermissionDenied("Content widget must have a layer assigned")
            
            template = layer.template
            if not template:
                logger.error(f"Layer {layer.id} has no template assigned")
                raise PermissionDenied("Content widget layer must have a template assigned")
            
            # Check permissions
            if not RolePermissions.can_edit_resource(user, template):
                raise PermissionDenied("You do not have permission to edit this content")
            
        except AttributeError as e:
            logger.error(f"Error accessing content relationships during update: {str(e)}", exc_info=True)
            logger.error(f"Content ID: {content.id}, Widget: {getattr(content, 'widget', None)}, "
                        f"Layer: {getattr(getattr(content, 'widget', None), 'layer', None) if content.widget else None}")
            raise PermissionDenied("Error checking permissions. Content may have invalid relationships. Please contact support.")
        except PermissionDenied:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during content update permission check: {str(e)}", exc_info=True)
            raise PermissionDenied(f"Error updating content: {str(e)}")
        
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
        
        Request body (optional):
        - screen_id: UUID of screen to retry download to (if not provided, retries to all screens using this content)
        - max_retries: Maximum number of retry attempts (default: 3)
        """
        content = self.get_object()
        user = request.user
        
        logger.info(f"Retry download request for content {content.id} by user {user.id if hasattr(user, 'id') else 'anonymous'}")
        logger.debug(f"Request data: {request.data}")
        logger.debug(f"Content download_status: {content.download_status}, retry_count: {content.retry_count}")
        
        # Check permissions - verify user has access to this content
        try:
            from .storage import ContentStorageManager
            if not ContentStorageManager.verify_user_access(content, user):
                logger.warning(f"User {user.id if hasattr(user, 'id') else 'anonymous'} denied access to content {content.id}")
                raise PermissionDenied("You do not have permission to retry download for this content")
        except PermissionDenied:
            raise
        except (AttributeError, Exception) as e:
            logger.error(f"Error checking permissions for retry download: {e}", exc_info=True)
            raise PermissionDenied("You do not have permission to retry download for this content")
        
        screen_id = request.data.get('screen_id')
        max_retries = request.data.get('max_retries', 3)
        
        logger.debug(f"Received screen_id: {screen_id} (type: {type(screen_id)})")
        logger.debug(f"Received max_retries: {max_retries} (type: {type(max_retries)})")
        
        # Handle empty string or None
        if screen_id == '' or screen_id is None:
            screen_id = None
            logger.info("No screen_id provided, will retry to all screens using this content")
        
        # Validate max_retries
        try:
            max_retries = int(max_retries)
            if max_retries < 1:
                max_retries = 3
        except (ValueError, TypeError):
            max_retries = 3
        
        # If screen_id is provided, retry to that specific screen
        if screen_id:
            # Validate screen_id format (should be UUID)
            try:
                import uuid
                uuid.UUID(str(screen_id))
            except (ValueError, AttributeError):
                return Response(
                    {'error': f'Invalid screen_id format: {screen_id}. Must be a valid UUID.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from signage.models import Screen
            try:
                screen = Screen.objects.get(id=screen_id)
            except Screen.DoesNotExist:
                return Response(
                    {'error': f'Screen not found with id: {screen_id}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"Error fetching screen {screen_id}: {str(e)}")
                return Response(
                    {'error': f'Error fetching screen: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Check if user can access the screen
            if not RolePermissions.can_view_resource(user, screen):
                raise PermissionDenied("You do not have permission to access this screen")
            
            # Check if screen is online
            if not screen.is_online:
                return Response({
                    'status': 'error',
                    'message': f'Screen "{screen.name}" is not online. Cannot download content to offline screen.',
                    'content_id': str(content.id),
                    'screen_id': str(screen.id),
                    'screen_online': screen.is_online
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if content has file_url (required for download)
            if not content.file_url and content.type in ['image', 'video', 'webview']:
                return Response({
                    'status': 'error',
                    'message': f'Content "{content.name}" has no file URL. Please upload a file first.',
                    'content_id': str(content.id),
                    'screen_id': str(screen.id),
                    'content_type': content.type
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if content is active
            if not content.is_active:
                return Response({
                    'status': 'error',
                    'message': f'Content "{content.name}" is not active. Cannot download inactive content.',
                    'content_id': str(content.id),
                    'screen_id': str(screen.id),
                    'is_active': content.is_active
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                logger.info(f"Attempting retry download for content {content.id} to screen {screen.id}")
                logger.debug(f"Content status: {content.download_status}, retry_count: {content.retry_count}, max_retries: {max_retries}")
                
                # Check if content can be retried
                if content.download_status not in ['failed', 'pending']:
                    error_msg = f'Cannot retry download: content status is "{content.download_status}" (must be "failed" or "pending")'
                    logger.warning(f"Retry download blocked: {error_msg}")
                    return Response({
                        'status': 'error',
                        'message': error_msg,
                        'content_id': str(content.id),
                        'screen_id': str(screen.id),
                        'download_status': content.download_status
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check retry count
                if content.retry_count >= max_retries:
                    error_msg = f'Maximum retry attempts ({max_retries}) exceeded. Current retry count: {content.retry_count}'
                    logger.warning(f"Retry download blocked: {error_msg}")
                    return Response({
                        'status': 'error',
                        'message': error_msg,
                        'content_id': str(content.id),
                        'screen_id': str(screen.id),
                        'retry_count': content.retry_count,
                        'max_retries': max_retries
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                logger.info(f"Calling content.retry_download() for content {content.id} to screen {screen.id}")
                success = content.retry_download(screen, max_retries=max_retries)
                logger.info(f"Retry download result: {success} for content {content.id} to screen {screen.id}")
                
                # Refresh content from DB to get updated status
                content.refresh_from_db()
                
                if success:
                    return Response({
                        'status': 'success',
                        'message': f'Content "{content.name}" retry download successful to screen "{screen.name}"',
                        'content_id': str(content.id),
                        'screen_id': str(screen.id),
                        'download_status': content.download_status,
                        'retry_count': content.retry_count
                    }, status=status.HTTP_200_OK)
                else:
                    # Get more details about why it failed
                    error_msg = 'Retry download failed'
                    if content.download_status == 'success':
                        error_msg = 'Content is already successfully downloaded'
                    elif content.retry_count >= max_retries:
                        error_msg = f'Maximum retry attempts ({max_retries}) exceeded'
                    else:
                        error_msg = f'Retry download failed (retry count: {content.retry_count}/{max_retries})'
                    
                    logger.warning(f"Retry download returned False for content {content.id} to screen {screen.id}: {error_msg}")
                    return Response({
                        'status': 'error',
                        'message': error_msg,
                        'content_id': str(content.id),
                        'screen_id': str(screen.id),
                        'download_status': content.download_status,
                        'retry_count': content.retry_count
                    }, status=status.HTTP_400_BAD_REQUEST)
            except ValueError as e:
                # Handle validation errors from download_to_screen
                error_msg = str(e)
                logger.warning(f"Validation error during retry download for content {content.id} to screen {screen.id}: {error_msg}")
                return Response({
                    'status': 'error',
                    'message': error_msg,
                    'content_id': str(content.id),
                    'screen_id': str(screen.id),
                    'error_type': 'ValidationError'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                error_msg = f'Retry download failed: {str(e)}'
                logger.error(f"Error during retry download for content {content.id} to screen {screen.id}: {error_msg}", exc_info=True)
                return Response({
                    'status': 'error',
                    'message': error_msg,
                    'content_id': str(content.id),
                    'screen_id': str(screen.id),
                    'error_type': type(e).__name__
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # No screen_id provided - retry to all screens that use this content
            try:
                # Get all screens that have this content's template active
                widget = content.widget
                if not widget:
                    return Response({
                        'error': 'Content has no widget assigned'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                layer = widget.layer
                if not layer:
                    return Response({
                        'error': 'Content widget has no layer assigned'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                template = layer.template
                if not template:
                    return Response({
                        'error': 'Content layer has no template assigned'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get all screens with this template
                from signage.models import Screen
                screens = Screen.objects.filter(active_template=template, is_online=True)
                
                if not screens.exists():
                    return Response({
                        'status': 'error',
                        'message': 'No online screens found with this template',
                        'content_id': str(content.id)
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Retry download to all screens
                results = []
                for screen in screens:
                    try:
                        success = content.retry_download(screen, max_retries=max_retries)
                        results.append({
                            'screen_id': str(screen.id),
                            'screen_name': screen.name,
                            'success': success,
                            'download_status': content.download_status
                        })
                    except Exception as e:
                        logger.error(f"Error retrying download to screen {screen.id}: {str(e)}")
                        results.append({
                            'screen_id': str(screen.id),
                            'screen_name': screen.name,
                            'success': False,
                            'error': str(e)
                        })
                
                success_count = sum(1 for r in results if r.get('success'))
                
                return Response({
                    'status': 'success' if success_count > 0 else 'partial',
                    'message': f'Retry download completed: {success_count}/{len(results)} screens successful',
                    'content_id': str(content.id),
                    'results': results
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"Error during bulk retry download: {str(e)}", exc_info=True)
                return Response({
                    'status': 'error',
                    'message': f'Retry download failed: {str(e)}',
                    'content_id': str(content.id)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request, id=None):
        """
        POST /api/contents/{id}/upload/
        Upload a file for content.
        Requires multipart/form-data with 'file' field.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Upload request received for content ID: {id}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Request FILES keys: {list(request.FILES.keys()) if request.FILES else 'EMPTY'}")
        logger.info(f"Request POST keys: {list(request.POST.keys()) if request.POST else 'EMPTY'}")
        
        content = self.get_object()
        user = request.user
        
        logger.info(f"Content found: {content.id} ({content.name}), Type: {content.type}")
        logger.info(f"User: {user.id if hasattr(user, 'id') else 'Anonymous'} ({user.username if hasattr(user, 'username') else 'N/A'})")
        
        # Check permissions with proper null checks
        try:
            widget = content.widget
            if not widget:
                logger.error(f"Content {content.id} has no widget assigned")
                return Response(
                    {'error': 'Content must have a widget assigned'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            layer = widget.layer
            if not layer:
                logger.error(f"Widget {widget.id} has no layer assigned")
                return Response(
                    {'error': 'Content widget must have a layer assigned'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            template = layer.template
            if not template:
                logger.error(f"Layer {layer.id} has no template assigned")
                return Response(
                    {'error': 'Content widget layer must have a template assigned'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check permissions
            if not RolePermissions.can_edit_resource(user, template):
                raise PermissionDenied("You do not have permission to upload content for this widget")
                
        except AttributeError as e:
            logger.error(f"Error accessing content relationships during upload: {str(e)}", exc_info=True)
            logger.error(f"Content ID: {content.id}, Widget: {getattr(content, 'widget', None)}, "
                        f"Layer: {getattr(getattr(content, 'widget', None), 'layer', None) if content.widget else None}")
            return Response(
                {'error': 'Error checking permissions. Content may have invalid relationships. Please contact support.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except PermissionDenied:
            raise
        
        # Check if file is provided
        if 'file' not in request.FILES:
            logger.error(f"Upload failed: No 'file' field in request.FILES. Available keys: {list(request.FILES.keys())}")
            logger.error(f"Request content type: {request.content_type}")
            logger.error(f"Request method: {request.method}")
            
            # Check if request body exists
            if hasattr(request, 'body'):
                logger.debug(f"Request body length: {len(request.body) if request.body else 0}")
            
            return Response(
                {
                    'error': 'File is required',
                    'message': 'Use multipart/form-data with "file" field.',
                    'received_fields': list(request.FILES.keys()) if request.FILES else [],
                    'content_type': request.content_type
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_obj = request.FILES['file']
        
        logger.info(f"File received: {file_obj.name}, Size: {file_obj.size} bytes, Type: {file_obj.content_type}")
        
        try:
            # Validate content before saving (comprehensive validation is done in storage.py)
            # Additional pre-save checks can be added here if needed
            
            logger.info(f"Starting file save process for content {content.id}")
            
            # Save uploaded file (includes comprehensive validation)
            metadata = content.save_uploaded_file(file_obj, user)
            
            logger.info(f"File saved successfully. Metadata: {metadata}")
            
            # Note: We don't log uploads to ContentDownloadLog as that's for screen-specific downloads
            # Uploads are logged via the content's created_at/updated_at timestamps
            
            # Build absolute URL for file_url
            absolute_file_url = content.file_url
            if content.file_url:
                if content.file_url.startswith('http'):
                    absolute_file_url = content.file_url
                else:
                    absolute_file_url = request.build_absolute_uri(content.file_url)
            
            return Response({
                'status': 'success',
                'message': f'File uploaded successfully for content "{content.name}"',
                'content_id': str(content.id),
                'file_url': content.file_url,
                'absolute_file_url': absolute_file_url,
                'file_size': content.file_size,
                'file_hash': content.file_hash,
                'storage_path': content.storage_path
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            error_msg = str(e)
            logger.error(f"Validation error during content upload: {error_msg}", exc_info=True)
            return Response({
                'status': 'error',
                'error': 'Validation failed',
                'message': error_msg,
                'content_id': str(content.id),
                'file_name': file_obj.name if file_obj else None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Unexpected error during content upload ({error_type}): {error_msg}", exc_info=True)
            return Response({
                'status': 'error',
                'error': 'Upload failed',
                'message': error_msg,
                'error_type': error_type,
                'content_id': str(content.id),
                'file_name': file_obj.name if file_obj else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, id=None):
        """
        GET /api/contents/{id}/preview/
        Get preview URL for content file.
        Returns media URL for local storage or signed URL for S3.
        """
        content = self.get_object()
        user = request.user
        
        # Check permissions
        try:
            template = content.widget.layer.template
            if not RolePermissions.can_view_resource(user, template):
                raise PermissionDenied("You do not have permission to preview this content")
        except (AttributeError, Exception) as e:
            logger.error(f"Error checking permissions for content preview: {e}")
            raise PermissionDenied("You do not have permission to preview this content")
        
        if not content.file_url and not content.storage_path:
            return Response(
                {'error': 'Content has no file to preview'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Get preview URL (no expiration for preview, or use short expiration)
            preview_url = content.get_secure_url(expiration=3600)  # 1 hour for preview
            
            return Response({
                'status': 'success',
                'content_id': str(content.id),
                'preview_url': preview_url,
                'content_type': content.type,
                'file_size': content.file_size,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating preview URL: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'message': f'Failed to generate preview URL: {str(e)}'
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
        
        # Check permissions - verify user has access to this content
        try:
            from .storage import ContentStorageManager
            if not ContentStorageManager.verify_user_access(content, user):
                raise PermissionDenied("You do not have permission to download this content")
        except PermissionDenied:
            raise
        except (AttributeError, Exception) as e:
            logger.error(f"Error checking permissions for content download: {e}")
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
