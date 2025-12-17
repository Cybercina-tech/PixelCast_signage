from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db.models import Q
from django.utils import timezone as django_timezone
from datetime import timedelta

from .models import Screen
from .serializers import (
    ScreenSerializer, HeartbeatSerializer, CommandSerializer,
    CommandPullSerializer, CommandResponseSerializer, ContentSyncSerializer,
    TemplateSerializer, TemplateContentSerializer
)
from commands.models import Command
from templates.models import Template, Content
from log.models import CommandExecutionLog, ScreenStatusLog, ContentDownloadLog


class ScreenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Screen model.
    Provides standard CRUD operations for screens.
    """
    queryset = Screen.objects.all()
    serializer_class = ScreenSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by owner if user is not staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def heartbeat(self, request, id=None):
        """
        POST /api/screens/{id}/heartbeat/
        Alternative endpoint for heartbeat (using screen ID)
        """
        try:
            screen = self.get_object()
        except Screen.DoesNotExist:
            return Response(
                {'error': 'Screen not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = HeartbeatSerializer(data=request.data)
        if serializer.is_valid():
            screen = serializer.validated_data['screen']
            
            # Get IP address from request
            ip_address = self._get_client_ip(request)
            
            # Update heartbeat
            screen.update_heartbeat(
                latency=serializer.validated_data.get('latency'),
                cpu_usage=serializer.validated_data.get('cpu_usage'),
                memory_usage=serializer.validated_data.get('memory_usage'),
                ip_address=ip_address
            )
            
            # Update optional device information
            update_fields = []
            if 'app_version' in serializer.validated_data:
                screen.app_version = serializer.validated_data['app_version']
                update_fields.append('app_version')
            if 'os_version' in serializer.validated_data:
                screen.os_version = serializer.validated_data['os_version']
                update_fields.append('os_version')
            if 'device_model' in serializer.validated_data:
                screen.device_model = serializer.validated_data['device_model']
                update_fields.append('device_model')
            if 'screen_width' in serializer.validated_data:
                screen.screen_width = serializer.validated_data['screen_width']
                update_fields.append('screen_width')
            if 'screen_height' in serializer.validated_data:
                screen.screen_height = serializer.validated_data['screen_height']
                update_fields.append('screen_height')
            if 'brightness' in serializer.validated_data:
                screen.brightness = serializer.validated_data['brightness']
                update_fields.append('brightness')
            if 'orientation' in serializer.validated_data:
                screen.orientation = serializer.validated_data['orientation']
                update_fields.append('orientation')
            
            if update_fields:
                screen.save(update_fields=update_fields)
            
            return Response({
                'status': 'success',
                'message': 'Heartbeat received',
                'screen_id': str(screen.id),
                'is_online': screen.is_online,
                'last_heartbeat_at': screen.last_heartbeat_at
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def heartbeat_endpoint(request):
    """
    POST /api/screens/heartbeat/
    Endpoint for Screens to send heartbeat.
    Authenticates using auth_token and secret_key.
    """
    serializer = HeartbeatSerializer(data=request.data)
    if serializer.is_valid():
        screen = serializer.validated_data['screen']
        
        # Get IP address from request
        ip_address = _get_client_ip(request)
        
        # Update heartbeat
        screen.update_heartbeat(
            latency=serializer.validated_data.get('latency'),
            cpu_usage=serializer.validated_data.get('cpu_usage'),
            memory_usage=serializer.validated_data.get('memory_usage'),
            ip_address=ip_address
        )
        
        # Update optional device information
        update_fields = []
        if 'app_version' in serializer.validated_data:
            screen.app_version = serializer.validated_data['app_version']
            update_fields.append('app_version')
        if 'os_version' in serializer.validated_data:
            screen.os_version = serializer.validated_data['os_version']
            update_fields.append('os_version')
        if 'device_model' in serializer.validated_data:
            screen.device_model = serializer.validated_data['device_model']
            update_fields.append('device_model')
        if 'screen_width' in serializer.validated_data:
            screen.screen_width = serializer.validated_data['screen_width']
            update_fields.append('screen_width')
        if 'screen_height' in serializer.validated_data:
            screen.screen_height = serializer.validated_data['screen_height']
            update_fields.append('screen_height')
        if 'brightness' in serializer.validated_data:
            screen.brightness = serializer.validated_data['brightness']
            update_fields.append('brightness')
        if 'orientation' in serializer.validated_data:
            screen.orientation = serializer.validated_data['orientation']
            update_fields.append('orientation')
        
        if update_fields:
            screen.save(update_fields=update_fields)
        
        return Response({
            'status': 'success',
            'message': 'Heartbeat received',
            'screen_id': str(screen.id),
            'is_online': screen.is_online,
            'last_heartbeat_at': screen.last_heartbeat_at
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def command_pull_endpoint(request):
    """
    GET /api/screens/command-pull/
    Endpoint for Screens to fetch pending commands.
    Returns pending commands ordered by priority and creation time.
    """
    serializer = CommandPullSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    screen = serializer.validated_data['screen']
    limit = serializer.validated_data.get('limit', 10)
    
    # Get pending commands for this screen
    commands = Command.objects.filter(
        screen=screen,
        status='pending'
    ).exclude(
        # Exclude expired commands
        expire_at__lt=timezone.now()
    ).order_by(
        '-priority',
        'created_at'
    )[:limit]
    
    # Mark commands as being processed
    now = timezone.now()
    for command in commands:
        command.last_attempt_at = now
        command.attempt_count += 1
        command.save(update_fields=['last_attempt_at', 'attempt_count'])
        
        # Create execution log entry
        CommandExecutionLog.objects.create(
            command=command,
            screen=screen,
            status='running',
            started_at=now
        )
    
    # Update screen's last_command_sent_at
    if commands.exists():
        screen.last_command_sent_at = now
        screen.is_busy = True
        screen.save(update_fields=['last_command_sent_at', 'is_busy'])
    
    command_serializer = CommandSerializer(commands, many=True)
    
    return Response({
        'status': 'success',
        'commands': command_serializer.data,
        'count': len(command_serializer.data)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def command_response_endpoint(request):
    """
    POST /api/screens/command-response/
    Endpoint for Screens to send command execution responses.
    Updates command status and creates execution log entry.
    """
    serializer = CommandResponseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    screen = serializer.validated_data['screen']
    command = serializer.validated_data['command']
    response_status = serializer.validated_data['status']
    response_payload = serializer.validated_data.get('response_payload', {})
    error_message = serializer.validated_data.get('error_message', '')
    
    # Update command status
    if response_status == 'done':
        command.mark_done()
    else:
        command.mark_failed()
    
    # Update screen's last_command_received_at and is_busy
    screen.last_command_received_at = timezone.now()
    screen.is_busy = False
    screen.save(update_fields=['last_command_received_at', 'is_busy'])
    
    # Update or create execution log entry
    exec_log = CommandExecutionLog.objects.filter(
        command=command,
        screen=screen,
        status='running'
    ).order_by('-started_at').first()
    
    if exec_log:
        exec_log.status = response_status
        exec_log.finished_at = timezone.now()
        exec_log.response_payload = response_payload
        if error_message:
            exec_log.error_message = error_message
        exec_log.save(update_fields=['status', 'finished_at', 'response_payload', 'error_message'])
    else:
        # Create new log entry if none exists
        CommandExecutionLog.objects.create(
            command=command,
            screen=screen,
            status=response_status,
            started_at=command.last_attempt_at or timezone.now(),
            finished_at=timezone.now(),
            response_payload=response_payload,
            error_message=error_message
        )
    
    return Response({
        'status': 'success',
        'message': 'Command response recorded',
        'command_id': str(command.id),
        'command_status': command.status
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_endpoint(request):
    """
    GET /api/screens/health-check/
    Endpoint for Screens to perform health check.
    Returns comprehensive health status information.
    """
    auth_token = request.query_params.get('auth_token')
    secret_key = request.query_params.get('secret_key')
    
    if not auth_token or not secret_key:
        return Response(
            {'error': 'auth_token and secret_key are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        screen = Screen.objects.get(auth_token=auth_token)
    except Screen.DoesNotExist:
        return Response(
            {'error': 'Invalid authentication token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not screen.authenticate(auth_token, secret_key):
        return Response(
            {'error': 'Invalid secret key'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Perform health check
    health = screen.health_check()
    
    return Response({
        'status': 'success',
        'screen_id': str(screen.id),
        'screen_name': screen.name,
        'health': health
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def content_sync_endpoint(request):
    """
    POST /api/screens/content-sync/
    Endpoint for Screens to report content download status or request content sync.
    
    Supports two sync types:
    1. 'request': Screen requests content sync for specific content IDs or all active template content
    2. 'status': Screen reports download status for content items
    """
    serializer = ContentSyncSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    screen = serializer.validated_data['screen']
    sync_type = serializer.validated_data['sync_type']
    
    if sync_type == 'request':
        # Screen is requesting content sync
        content_ids = serializer.validated_data.get('content_ids', [])
        
        if not screen.active_template:
            return Response({
                'status': 'error',
                'message': 'No active template assigned to this screen'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get content to sync
        if content_ids:
            # Sync specific content items
            contents = Content.objects.filter(
                id__in=content_ids,
                widget__layer__template=screen.active_template,
                is_active=True
            )
        else:
            # Sync all active template content
            contents = screen.active_template.get_all_contents().filter(is_active=True)
        
        # Prepare content list for response
        content_list = []
        for content in contents:
            content_list.append({
                'id': str(content.id),
                'name': content.name,
                'type': content.type,
                'file_url': content.file_url,
                'content_json': content.content_json,
                'duration': content.duration,
                'order': content.order,
                'download_status': content.download_status
            })
        
        return Response({
            'status': 'success',
            'message': 'Content sync request processed',
            'template_id': str(screen.active_template.id),
            'template_name': screen.active_template.name,
            'contents': content_list,
            'count': len(content_list)
        }, status=status.HTTP_200_OK)
    
    elif sync_type == 'status':
        # Screen is reporting download status
        download_status = serializer.validated_data.get('download_status', [])
        
        synced_count = 0
        failed_count = 0
        
        for status_item in download_status:
            content_id = status_item.get('content_id')
            item_status = status_item.get('status')
            file_size = status_item.get('file_size')
            error_message = status_item.get('error_message', '')
            
            try:
                content = Content.objects.get(id=content_id)
            except Content.DoesNotExist:
                continue
            
            # Update content download status
            if item_status == 'success':
                content.mark_downloaded()
                synced_count += 1
            elif item_status == 'failed':
                content.mark_failed()
                failed_count += 1
            else:
                content.update_status('pending')
            
            # Create or update download log
            download_log = ContentDownloadLog.objects.filter(
                content=content,
                screen=screen
            ).order_by('-created_at').first()
            
            if download_log:
                download_log.status = item_status
                if file_size:
                    download_log.file_size = file_size
                if error_message:
                    download_log.error_message = error_message
                if item_status == 'success':
                    download_log.downloaded_at = timezone.now()
                download_log.save()
            else:
                ContentDownloadLog.objects.create(
                    content=content,
                    screen=screen,
                    status=item_status,
                    file_size=file_size,
                    error_message=error_message,
                    downloaded_at=timezone.now() if item_status == 'success' else None
                )
        
        return Response({
            'status': 'success',
            'message': 'Content download status updated',
            'synced_count': synced_count,
            'failed_count': failed_count,
            'total_reported': len(download_status)
        }, status=status.HTTP_200_OK)
    
    return Response({
        'status': 'error',
        'message': 'Invalid sync_type'
    }, status=status.HTTP_400_BAD_REQUEST)


def _get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
