from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django.utils import timezone as django_timezone
from django.views.decorators.csrf import csrf_exempt
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


@csrf_exempt  # Bypass CSRF protection for IoT devices
@api_view(['POST', 'OPTIONS'])  # CRITICAL: Must include POST and OPTIONS for CORS preflight
@authentication_classes([])  # Explicitly disable ALL authentication - override global REST_FRAMEWORK settings
@permission_classes([AllowAny])  # Explicitly allow any request - override global IsAuthenticated
def heartbeat_endpoint(request):
    """
    POST /iot/screens/heartbeat/ or /api/screens/heartbeat/
    
    THE IoT ESCAPE PLAN: Explicitly overrides global REST_FRAMEWORK authentication and permission settings.
    Uses @authentication_classes([]) and @permission_classes([AllowAny]) to bypass
    the global IsAuthenticated requirement in settings.py.
    
    Supports multiple authentication methods:
    1. screen_id (direct lookup)
    2. auth_token + secret_key (credential-based authentication)
    3. URL query parameters
    4. Environment variables (for screens that can't send credentials)
    """
    print(f"IoT Request received at: {request.path}")
    print(">>> HEARTBEAT REACHED THE VIEW <<<")
    
    import json
    import logging
    import os
    from django.http import JsonResponse
    
    logger = logging.getLogger(__name__)
    
    # Extract credentials from all possible sources
    screen_id = None
    auth_token = None
    secret_key = None
    
    # Try request.data first (DRF parsed JSON)
    if request.data and isinstance(request.data, dict):
        screen_id = request.data.get('screen_id')
        auth_token = request.data.get('auth_token')
        secret_key = request.data.get('secret_key')
    
    # Fallback: Try request.body (raw JSON)
    if not screen_id and not auth_token and hasattr(request, 'body') and request.body:
        try:
            raw_body = json.loads(request.body.decode('utf-8'))
            if isinstance(raw_body, dict):
                screen_id = screen_id or raw_body.get('screen_id')
                auth_token = auth_token or raw_body.get('auth_token')
                secret_key = secret_key or raw_body.get('secret_key')
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    
    # Fallback: Try query params
    if hasattr(request, 'query_params'):
        screen_id = screen_id or request.query_params.get('screen_id')
        auth_token = auth_token or request.query_params.get('auth_token')
        secret_key = secret_key or request.query_params.get('secret_key')
    if not screen_id and not auth_token:
        screen_id = screen_id or request.GET.get('screen_id')
        auth_token = auth_token or request.GET.get('auth_token')
        secret_key = secret_key or request.GET.get('secret_key')
    
    # Fallback: Try environment variables (for screens that can't send credentials)
    if not screen_id and not auth_token:
        screen_id = os.environ.get('SCREEN_ID')
        auth_token = os.environ.get('SCREEN_AUTH_TOKEN')
        secret_key = os.environ.get('SCREEN_SECRET_KEY')
    
    # Authenticate screen using available credentials
    screen = None
    auth_method = None
    
    try:
        # Method 1: Direct screen_id lookup (no authentication required)
        if screen_id:
            screen = Screen.objects.filter(id=screen_id).first()
            if screen:
                auth_method = 'screen_id'
                logger.info(f"Screen authenticated via screen_id: {screen.id}")
        
        # Method 2: auth_token + secret_key authentication
        if not screen and auth_token and secret_key:
            try:
                screen = Screen.objects.get(auth_token=auth_token)
                if screen.authenticate(auth_token, secret_key):
                    auth_method = 'auth_token'
                    logger.info(f"Screen authenticated via auth_token: {screen.id}")
                else:
                    logger.warning(f"Authentication failed: invalid secret_key for auth_token: {auth_token[:8]}...")
                    screen = None
            except Screen.DoesNotExist:
                logger.warning(f"No screen found with auth_token: {auth_token[:8] if auth_token else 'MISSING'}...")
                screen = None
            except Exception as e:
                logger.error(f"Error authenticating with auth_token: {e}", exc_info=True)
                screen = None
        
        # If no screen found, return 401
        if not screen:
            logger.warning(f"Heartbeat authentication failed from IP: {_get_client_ip(request)}")
            response = JsonResponse(
                {
                    'error': 'Authentication failed',
                    'message': 'Provide screen_id OR (auth_token + secret_key) in POST body, query params, or environment variables.'
                },
                status=401
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        # SUCCESS: Screen authenticated
        print(f"SUCCESS: Screen {screen.id} authenticated via {auth_method}")
        logger.info(f"SUCCESS: Screen {screen.id} authenticated via {auth_method}")
        
        # Get IP address from request
        ip_address = _get_client_ip(request)
        
        # Extract optional metrics from request data
        data_source = request.data if request.data and isinstance(request.data, dict) else {}
        if not data_source and hasattr(request, 'body') and request.body:
            try:
                data_source = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data_source = {}
        
        latency = data_source.get('latency')
        cpu_usage = data_source.get('cpu_usage')
        memory_usage = data_source.get('memory_usage')
        app_version = data_source.get('app_version')
        os_version = data_source.get('os_version')
        device_model = data_source.get('device_model')
        screen_width = data_source.get('screen_width')
        screen_height = data_source.get('screen_height')
        brightness = data_source.get('brightness')
        orientation = data_source.get('orientation')
        
        # CRITICAL: Update heartbeat status in database
        # This method sets is_online=True and last_heartbeat_at=now() and saves to database
        screen.update_heartbeat(
            latency=latency,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            ip_address=ip_address
        )
        
        # Refresh screen from database to ensure we have the latest status
        screen.refresh_from_db()
        
        # Log the updated status for debugging
        logger.info(f"Screen {screen.id} heartbeat updated - is_online: {screen.is_online}, last_heartbeat_at: {screen.last_heartbeat_at}")
        print(f"Screen {screen.id} status updated - is_online: {screen.is_online}, last_heartbeat_at: {screen.last_heartbeat_at}")
        
        # Update optional device information
        update_fields = []
        if app_version is not None:
            screen.app_version = app_version
            update_fields.append('app_version')
        if os_version is not None:
            screen.os_version = os_version
            update_fields.append('os_version')
        if device_model is not None:
            screen.device_model = device_model
            update_fields.append('device_model')
        if screen_width is not None:
            screen.screen_width = screen_width
            update_fields.append('screen_width')
        if screen_height is not None:
            screen.screen_height = screen_height
            update_fields.append('screen_height')
        if brightness is not None:
            screen.brightness = brightness
            update_fields.append('brightness')
        if orientation is not None:
            screen.orientation = orientation
            update_fields.append('orientation')
        
        if update_fields:
            screen.save(update_fields=update_fields)
        
        # Return success response with clean headers
        response_data = {
            'status': 'success',
            'message': 'Heartbeat received',
            'screen_id': str(screen.id),
            'is_online': screen.is_online,
            'last_heartbeat_at': screen.last_heartbeat_at.isoformat() if screen.last_heartbeat_at else None
        }
        
        response = JsonResponse(response_data, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing heartbeat for screen_id {screen_id}: {e}", exc_info=True)
        response = JsonResponse(
            {
                'error': 'Internal server error',
                'message': str(e)
            },
            status=500
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response


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


@csrf_exempt  # Bypass CSRF protection for IoT devices
@api_view(['GET', 'OPTIONS'])  # CRITICAL: Must include GET and OPTIONS for CORS preflight
@authentication_classes([])  # Explicitly disable ALL authentication - override global REST_FRAMEWORK settings
@permission_classes([AllowAny])  # Explicitly allow any request - override global IsAuthenticated
def iot_command_pull_endpoint(request):
    """
    GET /iot/commands/pending/
    
    THE IoT ESCAPE PLAN: Explicitly overrides global REST_FRAMEWORK authentication and permission settings.
    Uses @authentication_classes([]) and @permission_classes([AllowAny]) to bypass
    the global IsAuthenticated requirement in settings.py.
    ONLY validates screen_id exists in PostgreSQL.
    """
    print(f"IoT Request received at: {request.path}")
    print(">>> COMMAND PULL REACHED THE VIEW <<<")
    
    import json
    import logging
    from django.http import JsonResponse
    
    logger = logging.getLogger(__name__)
    
    # Extract screen_id from request
    screen_id = None
    
    # Try query params first
    if hasattr(request, 'query_params'):
        screen_id = request.query_params.get('screen_id')
    if not screen_id:
        screen_id = request.GET.get('screen_id')
    
    # Validate screen_id is provided
    if not screen_id:
        logger.warning(f"Command pull request missing screen_id from IP: {_get_client_ip(request)}")
        response = JsonResponse(
            {
                'error': 'screen_id is required',
                'message': 'Send screen_id as query parameter: ?screen_id=<uuid>'
            },
            status=400
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    # Look up screen in PostgreSQL database
    try:
        screen = Screen.objects.filter(id=screen_id).first()
        
        if not screen:
            logger.warning(f"Screen not found with screen_id: {screen_id}")
            response = JsonResponse(
                {
                    'error': 'Screen not found',
                    'message': f'No screen found with screen_id {screen_id}'
                },
                status=404
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        # Get limit from query params
        limit = 10
        try:
            limit_param = request.GET.get('limit', '10')
            limit = int(limit_param)
            if limit > 50:
                limit = 50  # Max 50 commands
        except (ValueError, TypeError):
            limit = 10
        
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
        
        # Mark commands as being processed (executing)
        now = timezone.now()
        command_list = []
        for command in commands:
            # Update command status to executing
            command.status = 'executing'
            command.executed_at = now
            command.last_attempt_at = now
            command.attempt_count += 1
            command.save(update_fields=['status', 'executed_at', 'last_attempt_at', 'attempt_count'])
            
            # Create execution log entry
            CommandExecutionLog.objects.create(
                command=command,
                screen=screen,
                status='running',
                started_at=now
            )
            
            # Serialize command
            command_list.append({
                'id': str(command.id),
                'type': command.type,
                'payload': command.payload or {},
                'priority': command.priority,
                'name': command.name or '',
                'created_at': command.created_at.isoformat() if command.created_at else None,
            })
        
        # Update screen's last_command_sent_at
        if commands.exists():
            screen.last_command_sent_at = now
            screen.is_busy = True
            screen.save(update_fields=['last_command_sent_at', 'is_busy'])
        
        logger.info(f"Screen {screen.id} fetched {len(command_list)} pending commands")
        
        response_data = {
            'status': 'success',
            'commands': command_list,
            'count': len(command_list)
        }
        
        response = JsonResponse(response_data, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
        
    except Exception as e:
        logger.error(f"Error in command pull endpoint: {str(e)}", exc_info=True)
        response = JsonResponse(
            {
                'error': 'Internal server error',
                'message': str(e)
            },
            status=500
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response


@csrf_exempt  # Bypass CSRF protection for IoT devices
@api_view(['POST', 'OPTIONS'])  # CRITICAL: Must include POST and OPTIONS for CORS preflight
@authentication_classes([])  # Explicitly disable ALL authentication - override global REST_FRAMEWORK settings
@permission_classes([AllowAny])  # Explicitly allow any request - override global IsAuthenticated
def iot_command_response_endpoint(request):
    """
    POST /iot/commands/{id}/status/
    
    THE IoT ESCAPE PLAN: Explicitly overrides global REST_FRAMEWORK authentication and permission settings.
    Uses @authentication_classes([]) and @permission_classes([AllowAny]) to bypass
    the global IsAuthenticated requirement in settings.py.
    ONLY validates screen_id exists in PostgreSQL.
    """
    print(f"IoT Request received at: {request.path}")
    print(">>> COMMAND RESPONSE REACHED THE VIEW <<<")
    
    import json
    import logging
    from django.http import JsonResponse
    
    logger = logging.getLogger(__name__)
    
    # Extract screen_id and command_id from request
    screen_id = None
    command_id = None
    
    # Try request.data first (DRF parsed JSON)
    if request.data and isinstance(request.data, dict):
        screen_id = request.data.get('screen_id')
        command_id = request.data.get('command_id')
    
    # Fallback: Try request.body (raw JSON)
    if (not screen_id or not command_id) and hasattr(request, 'body') and request.body:
        try:
            raw_body = json.loads(request.body.decode('utf-8'))
            if isinstance(raw_body, dict):
                screen_id = screen_id or raw_body.get('screen_id')
                command_id = command_id or raw_body.get('command_id')
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    
    # Validate required fields
    if not screen_id:
        response = JsonResponse(
            {
                'error': 'screen_id is required',
                'message': 'Send screen_id in POST body (JSON)'
            },
            status=400
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    if not command_id:
        response = JsonResponse(
            {
                'error': 'command_id is required',
                'message': 'Send command_id in POST body (JSON)'
            },
            status=400
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    # Look up screen and command
    try:
        screen = Screen.objects.filter(id=screen_id).first()
        
        if not screen:
            logger.warning(f"Screen not found with screen_id: {screen_id}")
            response = JsonResponse(
                {
                    'error': 'Screen not found',
                    'message': f'No screen found with screen_id {screen_id}'
                },
                status=404
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        command = Command.objects.filter(id=command_id, screen=screen).first()
        
        if not command:
            logger.warning(f"Command not found: {command_id} for screen: {screen_id}")
            response = JsonResponse(
                {
                    'error': 'Command not found',
                    'message': f'No command found with id {command_id} for screen {screen_id}'
                },
                status=404
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        # Get response status from request
        data_source = request.data if request.data and isinstance(request.data, dict) else {}
        if not data_source and hasattr(request, 'body') and request.body:
            try:
                data_source = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data_source = {}
        
        response_status = data_source.get('status', 'done')  # Default to 'done'
        error_message = data_source.get('error_message', '')
        response_payload = data_source.get('response_payload', {})
        
        # Validate status
        if response_status not in ['done', 'failed']:
            response_status = 'done'  # Default to done
        
        # Update command status
        now = timezone.now()
        if response_status == 'done':
            command.mark_done()
        else:
            command.mark_failed(error_message or 'Command execution failed')
        
        # Update screen
        screen.last_command_received_at = now
        screen.is_busy = False
        screen.save(update_fields=['last_command_received_at', 'is_busy'])
        
        # Update execution log
        exec_log = CommandExecutionLog.objects.filter(
            command=command,
            screen=screen,
            status='running'
        ).order_by('-started_at').first()
        
        if exec_log:
            exec_log.status = response_status
            exec_log.finished_at = now
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
                started_at=command.executed_at or now,
                finished_at=now,
                response_payload=response_payload,
                error_message=error_message
            )
        
        logger.info(f"Command {command_id} status updated to {response_status} by screen {screen_id}")
        
        response_data = {
            'status': 'success',
            'message': 'Command response recorded',
            'command_id': str(command.id),
            'command_status': command.status
        }
        
        response = JsonResponse(response_data, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
        
    except Exception as e:
        logger.error(f"Error in command response endpoint: {str(e)}", exc_info=True)
        response = JsonResponse(
            {
                'error': 'Internal server error',
                'message': str(e)
            },
            status=500
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response


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


@csrf_exempt  # Bypass CSRF protection for IoT devices
@api_view(['GET', 'OPTIONS'])  # CRITICAL: Must include GET and OPTIONS for CORS preflight
@authentication_classes([])  # Explicitly disable ALL authentication - override global REST_FRAMEWORK settings
@permission_classes([AllowAny])  # Explicitly allow any request - override global IsAuthenticated
def player_template_endpoint(request):
    """
    GET /iot/player/template/?screen_id=uuid-string or /api/player/template/?screen_id=uuid-string
    
    THE IoT ESCAPE PLAN: Explicitly overrides global REST_FRAMEWORK authentication and permission settings.
    Uses @authentication_classes([]) and @permission_classes([AllowAny]) to bypass
    the global IsAuthenticated requirement in settings.py.
    ONLY validates screen_id exists in PostgreSQL.
    """
    print(f"IoT Request received at: {request.path}")
    print(">>> TEMPLATE REQUEST REACHED THE VIEW <<<")
    
    import json
    import logging
    from django.http import JsonResponse
    
    logger = logging.getLogger(__name__)
    
    # Only accept GET
    if request.method != 'GET':
        response = JsonResponse(
            {'error': 'Method not allowed', 'message': 'Only GET method is allowed'},
            status=405
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    # Extract screen_id from query parameters (GET request)
    screen_id = request.GET.get('screen_id')
    
    # Validate screen_id is provided
    if not screen_id:
        logger.warning('Player template request missing screen_id')
        response = JsonResponse(
            {'error': 'screen_id is required', 'message': 'Send screen_id as query parameter: ?screen_id=uuid'},
            status=400
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    # Look up screen in PostgreSQL database
    # CRITICAL: Use select_related to ensure active_template is loaded in same query
    # This prevents N+1 queries and ensures we get the latest active_template value
    try:
        screen = Screen.objects.select_related('active_template').filter(id=screen_id).first()
        
        if not screen:
            logger.warning(f'Player template request with invalid screen_id: {screen_id}')
            response = JsonResponse(
                {'error': 'Screen not found', 'message': f'No screen found with screen_id {screen_id}'},
                status=404
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        # SUCCESS: Screen found in PostgreSQL - log connection
        print(f"SUCCESS: Screen {screen.id} authenticated via PostgreSQL")
        logger.info(f"SUCCESS: Screen {screen.id} authenticated via PostgreSQL")
        
        # Check if screen has active template
        if not screen.active_template:
            logger.info(f'Player template request for screen {screen.id}: No active template')
            response = JsonResponse({
                'status': 'no_template',
                'template': None
            }, status=200)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        template = screen.active_template
        logger.info(f'Player template request for screen {screen.id}: Template {template.id} ({template.name})')
        
        # Validate template has valid dimensions
        if not template.width or not template.height or template.width <= 0 or template.height <= 0:
            logger.error(f'Template {template.id} has invalid dimensions: {template.width}x{template.height}')
            response = JsonResponse({
                'status': 'error',
                'error': 'Template has invalid dimensions',
                'template': None
            }, status=200)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        # Use player template serializer with request context for absolute URLs
        # CRITICAL: @api_view decorator already wraps request as DRF Request
        # We can use the request directly - it's already a DRF Request object
        # The underlying Django request is available as request._request if needed
        
        # Log for debugging
        try:
            # Get underlying Django request for host/scheme info
            django_request = getattr(request, '_request', request)
            host = django_request.get_host() if hasattr(django_request, 'get_host') else 'unknown'
            scheme = django_request.scheme if hasattr(django_request, 'scheme') else 'http'
            logger.debug(f"Template serializer context: request host={host}, scheme={scheme}, path={request.path}")
        except Exception as e:
            logger.warning(f"Could not log request details: {e}")
        
        # Use request directly - @api_view already wrapped it as DRF Request
        serializer = PlayerTemplateSerializer(template, context={'request': request, 'screen': screen})
        template_data = serializer.data
        
        # Return success response with clean headers
        response = JsonResponse({
            'status': 'success',
            'screen_id': str(screen.id),
            'template': template_data
        }, status=200)
        
        # Ensure clean headers (no CORS issues)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing template request for screen_id {screen_id}: {e}", exc_info=True)
        response = JsonResponse(
            {
                'error': 'Internal server error',
                'message': str(e)
            },
            status=500
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response


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