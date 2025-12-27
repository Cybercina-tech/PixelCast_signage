from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django.utils import timezone as django_timezone
from datetime import timedelta
import secrets
import uuid

from .models import Screen, PairingSession
from .serializers import (
    ScreenSerializer, HeartbeatSerializer, CommandSerializer,
    CommandPullSerializer, CommandResponseSerializer, ContentSyncSerializer,
    TemplateSerializer, TemplateContentSerializer, PlayerTemplateSerializer,
    PairingSessionSerializer, PairingBindSerializer, PairingStatusSerializer
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
        user = self.request.user
        
        # SuperAdmin and Admin can see all screens
        if user.has_full_access():
            return queryset
        
        # Filter by owner for other users
        queryset = queryset.filter(owner=user)
        
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
@authentication_classes([])  # Explicitly disable user authentication - use screen-based auth instead
def heartbeat_endpoint(request):
    """
    POST /api/screens/heartbeat/
    Endpoint for Screens to send heartbeat.
    Authenticates using auth_token and secret_key.
    
    Note: This endpoint uses @authentication_classes([]) to disable DRF's default
    authentication, so credentials must be sent in the request body (JSON) or as form data.
    """
    """
    POST /api/screens/heartbeat/
    Endpoint for Screens to send heartbeat.
    Authenticates using auth_token and secret_key.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Log incoming request for debugging
    logger.info(f"Heartbeat request received from IP: {_get_client_ip(request)}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Request headers: {dict(request.headers) if hasattr(request, 'headers') else 'N/A'}")
    logger.info(f"Request data type: {type(request.data)}")
    logger.info(f"Request data: {request.data}")
    logger.info(f"Request data keys: {list(request.data.keys()) if hasattr(request.data, 'keys') else 'N/A'}")
    logger.info(f"Has request.body: {hasattr(request, 'body')}")
    if hasattr(request, 'body'):
        logger.info(f"Request body length: {len(request.body) if request.body else 0}")
        logger.info(f"Request body (first 500 chars): {request.body[:500].decode('utf-8', errors='ignore') if request.body else 'EMPTY'}")
    
    # Try to parse JSON body manually if request.data is empty
    import json
    raw_body = None
    if hasattr(request, 'body') and request.body:
        try:
            raw_body = json.loads(request.body.decode('utf-8'))
            logger.debug(f"Parsed raw body: {raw_body}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.debug(f"Failed to parse raw body as JSON: {e}")
    
    # Extract credentials - try multiple sources for compatibility
    # Support both methods: auth_token+secret_key (legacy) and screen_id (new)
    auth_token = None
    secret_key = None
    screen_id = None
    
    # Priority 1: request.data (POST body, JSON) - DRF parsed
    if request.data and isinstance(request.data, dict):
        auth_token = request.data.get('auth_token')
        secret_key = request.data.get('secret_key')
        screen_id = request.data.get('screen_id')
        if auth_token or secret_key or screen_id:
            logger.info("Extracted credentials from request.data (DRF parsed)")
    
    # Priority 1b: Raw JSON body (if request.data didn't work)
    if (not auth_token or not secret_key) and not screen_id and raw_body and isinstance(raw_body, dict):
        auth_token = raw_body.get('auth_token') or auth_token
        secret_key = raw_body.get('secret_key') or secret_key
        screen_id = raw_body.get('screen_id') or screen_id
        if auth_token or secret_key or screen_id:
            logger.info("Extracted credentials from raw JSON body")
    
    # Priority 2: request.POST (form data)
    if (not auth_token or not secret_key) and not screen_id:
        if hasattr(request, 'POST') and request.POST:
            auth_token = request.POST.get('auth_token') or auth_token
            secret_key = request.POST.get('secret_key') or secret_key
            screen_id = request.POST.get('screen_id') or screen_id
            if auth_token or secret_key or screen_id:
                logger.info("Extracted credentials from request.POST")
    
    # Priority 3: Query parameters (fallback, not recommended but supported)
    if (not auth_token or not secret_key) and not screen_id:
        if hasattr(request, 'query_params') and request.query_params:
            auth_token = request.query_params.get('auth_token') or auth_token
            secret_key = request.query_params.get('secret_key') or secret_key
            screen_id = request.query_params.get('screen_id') or screen_id
            if auth_token or secret_key or screen_id:
                logger.info("Extracted credentials from query_params (fallback)")
    
    # Log credentials status (masked)
    logger.info(f"Received auth_token: {auth_token[:8] + '...' if auth_token and len(auth_token) > 8 else ('MISSING' if not auth_token else auth_token)}")
    logger.info(f"Received secret_key: {'***' if secret_key else 'MISSING'}")
    logger.info(f"Received screen_id: {screen_id if screen_id else 'MISSING'}")
    logger.info(f"Auth token length: {len(auth_token) if auth_token else 0}")
    logger.info(f"Secret key length: {len(secret_key) if secret_key else 0}")
    
    # Log raw_body if it exists
    if raw_body:
        logger.info(f"Raw body parsed successfully: {type(raw_body)}, keys: {list(raw_body.keys()) if isinstance(raw_body, dict) else 'N/A'}")
    
    # Check if credentials are present (either auth_token+secret_key OR screen_id)
    # New method: Use screen_id if provided (after pairing, credentials are removed from localStorage)
    if screen_id:
        try:
            screen = Screen.objects.get(id=screen_id)
            # Use screen's stored credentials for authentication
            auth_token = screen.auth_token
            secret_key = screen.secret_key
            logger.info(f"Using screen_id method: Found screen {screen.id}, using stored credentials")
        except Screen.DoesNotExist:
            logger.warning(f"Screen with id {screen_id} not found")
            return Response(
                {
                    'error': 'Screen not found',
                    'message': f'No screen found with id {screen_id}'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching screen by id: {e}")
            return Response(
                {
                    'error': 'Invalid screen_id',
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Legacy method: Check if auth_token and secret_key are present
    if not auth_token or not secret_key:
        logger.warning("Heartbeat request missing credentials", extra={
            'has_auth_token': bool(auth_token),
            'has_secret_key': bool(secret_key),
            'content_type': request.content_type,
            'request_method': request.method
        })
        return Response(
            {
                'error': 'Authentication credentials are required',
                'message': 'Send auth_token and secret_key in POST body (JSON) or as form data.',
                'received': {
                    'has_auth_token': bool(auth_token),
                    'has_secret_key': bool(secret_key)
                }
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Prepare data for serializer
    heartbeat_data = {
        'auth_token': auth_token,
        'secret_key': secret_key
    }
    
    # Add optional fields from request.data or raw_body if available
    data_source = request.data if request.data and isinstance(request.data, dict) else (raw_body if raw_body else {})
    if data_source:
        optional_fields = ['latency', 'cpu_usage', 'memory_usage', 'app_version', 
                          'os_version', 'device_model', 'screen_width', 'screen_height', 
                          'brightness', 'orientation']
        for field in optional_fields:
            if field in data_source:
                heartbeat_data[field] = data_source[field]
                logger.debug(f"Added optional field {field} to heartbeat_data")
    
    serializer = HeartbeatSerializer(data=heartbeat_data)
    
    if not serializer.is_valid():
        # Log validation errors in detail
        errors = serializer.errors
        logger.error(f"Heartbeat validation failed: {errors}")
        
        # Check specific error types
        if 'auth_token' in errors:
            error_msg = errors['auth_token']
            if isinstance(error_msg, list):
                error_msg = error_msg[0] if error_msg else 'Invalid authentication token'
            logger.warning(f"Authentication token error: {error_msg}")
            
            # Try to find the screen to provide more context
            provided_token = request.data.get('auth_token', '')
            if provided_token:
                try:
                    screen = Screen.objects.get(auth_token=provided_token)
                    logger.info(f"Screen found with token, but authentication failed. Screen ID: {screen.id}, Name: {screen.name}")
                except Screen.DoesNotExist:
                    logger.warning(f"No screen found with provided auth_token: {provided_token[:8]}...")
                except Exception as e:
                    logger.error(f"Error checking screen: {e}")
        
        if 'secret_key' in errors:
            error_msg = errors['secret_key']
            if isinstance(error_msg, list):
                error_msg = error_msg[0] if error_msg else 'Invalid secret key'
            logger.warning(f"Secret key error: {error_msg}")
        
        # Return detailed error response
        return Response({
            'error': 'Authentication failed',
            'details': errors,
            'message': 'Invalid credentials. Please check auth_token and secret_key.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Validation successful
    screen = serializer.validated_data['screen']
    logger.info(f"Heartbeat authenticated successfully for screen: {screen.id} ({screen.name})")
    
    # Get IP address from request
    ip_address = _get_client_ip(request)
    
    # Update heartbeat
    screen.update_heartbeat(
        latency=serializer.validated_data.get('latency'),
        cpu_usage=serializer.validated_data.get('cpu_usage'),
        memory_usage=serializer.validated_data.get('memory_usage'),
        ip_address=ip_address
    )
    
    logger.info(f"Screen {screen.id} heartbeat updated. is_online: {screen.is_online}, last_heartbeat_at: {screen.last_heartbeat_at}")
    
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
        logger.debug(f"Updated device info fields: {update_fields}")
    
    logger.info(f"Heartbeat successful for screen {screen.id}. Returning response.")
    
    return Response({
        'status': 'success',
        'message': 'Heartbeat received',
        'screen_id': str(screen.id),
        'is_online': screen.is_online,
        'last_heartbeat_at': screen.last_heartbeat_at
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])  # Screen-based authentication via auth_token + secret_key
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
@authentication_classes([])  # Screen-based authentication via auth_token + secret_key
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
@authentication_classes([])  # Screen-based authentication via auth_token + secret_key
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
@authentication_classes([])  # Screen-based authentication via auth_token + secret_key
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


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])  # Explicitly disable user authentication - use screen-based auth instead
def player_template_endpoint(request):
    """
    GET /api/player/template/
    
    Returns complete template structure for player rendering.
    Authenticates via auth_token + secret_key query params.
    
    Response includes:
    - Template metadata (width, height, orientation)
    - Layers with positions and styling
    - Widgets with positions, styling, and type
    - Content with URLs and metadata
    """
    import logging
    logger = logging.getLogger(__name__)
    
    auth_token = request.query_params.get('auth_token')
    secret_key = request.query_params.get('secret_key')
    
    if not auth_token or not secret_key:
        logger.warning('Player template request missing auth credentials')
        return Response(
            {'error': 'auth_token and secret_key are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        screen = Screen.objects.get(auth_token=auth_token)
        logger.info(f'Player template request for screen: {screen.id} ({screen.name})')
    except Screen.DoesNotExist:
        logger.warning(f'Player template request with invalid auth_token: {auth_token[:8]}...')
        return Response(
            {'error': 'Invalid authentication token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not screen.authenticate(auth_token, secret_key):
        logger.warning(f'Player template request with invalid secret_key for screen: {screen.id}')
        return Response(
            {'error': 'Invalid secret key'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not screen.active_template:
        logger.info(f'Player template request for screen {screen.id}: No active template')
        return Response({
            'status': 'no_template',
            'template': None
        }, status=status.HTTP_200_OK)
    
    template = screen.active_template
    logger.info(f'Player template request for screen {screen.id}: Template {template.id} ({template.name})')
    
    # Validate template has valid dimensions
    if not template.width or not template.height or template.width <= 0 or template.height <= 0:
        logger.error(f'Template {template.id} has invalid dimensions: {template.width}x{template.height}')
        return Response({
            'status': 'error',
            'error': 'Template has invalid dimensions',
            'template': None
        }, status=status.HTTP_200_OK)
    
    # Get active layers count for logging
    active_layers = template.layers.filter(is_active=True)
    total_layers = template.layers.count()
    logger.info(f'Template {template.id}: {active_layers.count()}/{total_layers} active layers')
    
    # Count widgets and contents for logging
    total_widgets = 0
    total_contents = 0
    active_widgets = 0
    active_contents = 0
    
    for layer in active_layers:
        layer_widgets = layer.get_active_widgets()
        active_widgets += layer_widgets.count()
        total_widgets += layer.widgets.count()
        
        for widget in layer_widgets:
            widget_contents = widget.get_active_contents()
            active_contents += widget_contents.count()
            total_contents += widget.contents.count()
    
    logger.info(f'Template {template.id}: {active_widgets}/{total_widgets} active widgets, {active_contents}/{total_contents} active contents')
    
    # Use player template serializer with request context for absolute URLs
    serializer = PlayerTemplateSerializer(template, context={'request': request, 'screen': screen})
    template_data = serializer.data
    
    # Log final response structure
    layers_count = len(template_data.get('layers', []))
    widgets_count = sum(len(layer.get('widgets', [])) for layer in template_data.get('layers', []))
    contents_count = sum(
        len(widget.get('contents', []))
        for layer in template_data.get('layers', [])
        for widget in layer.get('widgets', [])
    )
    
    logger.info(f'Player template response for screen {screen.id}: {layers_count} layers, {widgets_count} widgets, {contents_count} contents')
    
    # Validate response is not empty
    if layers_count == 0:
        logger.warning(f'Template {template.id} has no active layers in response')
    if widgets_count == 0:
        logger.warning(f'Template {template.id} has no active widgets in response')
    if contents_count == 0:
        logger.warning(f'Template {template.id} has no active contents in response')
    
    # Additional validation: Check if template is actually renderable
    validation_errors = []
    if not template.width or template.width <= 0:
        validation_errors.append(f'Invalid template width: {template.width}')
    if not template.height or template.height <= 0:
        validation_errors.append(f'Invalid template height: {template.height}')
    if layers_count == 0:
        validation_errors.append('No active layers found')
    if widgets_count == 0:
        validation_errors.append('No active widgets found')
    if contents_count == 0:
        validation_errors.append('No active contents found')
    
    if validation_errors:
        logger.error(f'Template {template.id} validation failed: {", ".join(validation_errors)}')
        # Still return the template, but log the issues for debugging
    
    return Response({
        'status': 'success',
        'screen_id': str(screen.id),
        'template': template_data
    }, status=status.HTTP_200_OK)


# Pairing endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_pairing_session(request):
    """
    POST /api/pairing/generate/
    
    Generate a new pairing session for TV/Web Player.
    Returns 6-digit code and pairing token for QR code.
    """
    # Generate 6-digit code (ensure uniqueness)
    max_attempts = 10
    for _ in range(max_attempts):
        pairing_code = str(secrets.randbelow(900000) + 100000)  # 100000-999999
        if not PairingSession.objects.filter(
            pairing_code=pairing_code,
            status='pending',
            expires_at__gt=timezone.now()
        ).exists():
            break
    else:
        return Response(
            {'error': 'Failed to generate unique pairing code. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Generate secure pairing token
    pairing_token = secrets.token_urlsafe(32)
    
    # Create pairing session (expires in 5 minutes)
    expires_at = timezone.now() + timedelta(minutes=5)
    session = PairingSession.objects.create(
        pairing_code=pairing_code,
        pairing_token=pairing_token,
        expires_at=expires_at,
        status='pending'
    )
    
    serializer = PairingSessionSerializer(session)
    return Response({
        'status': 'success',
        'pairing_session': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_pairing_status(request):
    """
    GET /api/pairing/status/?pairing_token=XXX
    
    Check the status of a pairing session (for TV polling).
    Returns status and screen credentials if paired.
    """
    serializer = PairingStatusSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    session = serializer.validated_data['pairing_token']
    
    # Check if paired
    if session.status == 'paired' and session.screen:
        return Response({
            'status': 'paired',
            'screen_id': str(session.screen.id),
            'auth_token': session.screen.auth_token,
            'secret_key': session.screen.secret_key,
            'screen_name': session.screen.name,
            'paired_at': session.paired_at
        }, status=status.HTTP_200_OK)
    
    # Still pending
    if session.status == 'pending':
        session_serializer = PairingSessionSerializer(session)
        return Response({
            'status': 'pending',
            'pairing_session': session_serializer.data
        }, status=status.HTTP_200_OK)
    
    # Expired or invalid
    return Response({
        'status': session.status,
        'message': 'Pairing session has expired or is invalid'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bind_pairing_session(request):
    """
    POST /api/pairing/bind/
    
    Bind a pairing session to the authenticated user.
    Creates a new Screen and links it to the user.
    
    Uses transaction.atomic() to ensure data integrity:
    - Screen creation and pairing session update are atomic
    - Prevents race conditions in PostgreSQL's strict transaction model
    """
    from django.db import transaction
    
    serializer = PairingBindSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    session = serializer.validated_data['session']
    screen_name = serializer.validated_data.get('screen_name', '')
    
    # Check if session is still valid
    if not session.is_valid():
        return Response({
            'error': 'Pairing session has expired or is invalid'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if already paired (do this before transaction to avoid unnecessary locking)
    if session.status != 'pending':
        return Response({
            'error': 'This pairing code/token has already been used'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Use atomic transaction to ensure screen creation and pairing are atomic
    # PostgreSQL's strict transaction handling will prevent race conditions
    try:
        with transaction.atomic():
            # Lock the session row to prevent concurrent pairing attempts
            session = PairingSession.objects.select_for_update().get(
                id=session.id,
                status='pending'
            )
            
            # Verify it's still valid (double-check after lock)
            if not session.is_valid():
                return Response({
                    'error': 'Pairing session has expired or is invalid'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create new screen
            screen = Screen.objects.create(
                name=screen_name or f"Screen {session.pairing_code}",
                device_id=f"device_{uuid.uuid4().hex[:16]}",
                owner=request.user,
                is_online=False  # Will be set to True when first heartbeat is received
            )
            
            # Mark session as paired (this updates status atomically)
            session.mark_paired(screen, request.user)
            
    except PairingSession.DoesNotExist:
        return Response({
            'error': 'Pairing session not found or already used'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Return screen info
    screen_serializer = ScreenSerializer(screen)
    return Response({
        'status': 'success',
        'message': 'Screen paired successfully',
        'screen': screen_serializer.data,
        'pairing_code': session.pairing_code
    }, status=status.HTTP_200_OK)