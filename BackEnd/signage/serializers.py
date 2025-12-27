from rest_framework import serializers
from django.utils import timezone
from .models import Screen, PairingSession
from commands.models import Command
from templates.models import Template, Content, Layer, Widget
from log.models import CommandExecutionLog, ScreenStatusLog, ContentDownloadLog


class ScreenSerializer(serializers.ModelSerializer):
    """Serializer for Screen model"""
    is_heartbeat_stale = serializers.SerializerMethodField()
    online_duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = Screen
        fields = [
            'id', 'name', 'device_id', 'location', 'description',
            'active_template', 'is_online', 'last_heartbeat_at',
            'last_ip', 'app_version', 'os_version', 'device_model',
            'screen_width', 'screen_height', 'brightness', 'orientation',
            'is_busy', 'is_heartbeat_stale', 'online_duration_seconds',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_online', 'last_heartbeat_at', 'last_ip',
            'is_busy', 'created_at', 'updated_at'
        ]
    
    def get_is_heartbeat_stale(self, obj):
        """Check if heartbeat is stale"""
        return obj.is_heartbeat_stale()
    
    def get_online_duration_seconds(self, obj):
        """Calculate online duration in seconds"""
        if not obj.is_online or not obj.last_heartbeat_at:
            return None
        delta = timezone.now() - obj.last_heartbeat_at
        return int(delta.total_seconds())


class HeartbeatSerializer(serializers.Serializer):
    """Serializer for heartbeat POST requests"""
    auth_token = serializers.CharField(required=True, write_only=True)
    secret_key = serializers.CharField(required=True, write_only=True)
    latency = serializers.FloatField(required=False, allow_null=True)
    cpu_usage = serializers.FloatField(required=False, allow_null=True, min_value=0, max_value=100)
    memory_usage = serializers.FloatField(required=False, allow_null=True, min_value=0, max_value=100)
    app_version = serializers.CharField(required=False, allow_blank=True, max_length=50)
    os_version = serializers.CharField(required=False, allow_blank=True, max_length=100)
    device_model = serializers.CharField(required=False, allow_blank=True, max_length=255)
    screen_width = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    screen_height = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    brightness = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=100)
    orientation = serializers.ChoiceField(required=False, choices=Screen.ORIENTATION_CHOICES)
    
    def validate(self, attrs):
        """Validate authentication credentials"""
        import logging
        logger = logging.getLogger(__name__)
        
        auth_token = attrs.get('auth_token')
        secret_key = attrs.get('secret_key')
        
        # Log validation attempt (masked)
        logger.debug(f"HeartbeatSerializer validation: auth_token={auth_token[:8] + '...' if auth_token else 'MISSING'}, secret_key={'***' if secret_key else 'MISSING'}")
        
        # Check if credentials are provided
        if not auth_token or not auth_token.strip():
            logger.warning("HeartbeatSerializer: auth_token is missing or empty")
            raise serializers.ValidationError({'auth_token': 'Authentication token is required'})
        
        if not secret_key or not secret_key.strip():
            logger.warning("HeartbeatSerializer: secret_key is missing or empty")
            raise serializers.ValidationError({'secret_key': 'Secret key is required'})
        
        try:
            screen = Screen.objects.get(auth_token=auth_token)
            logger.debug(f"HeartbeatSerializer: Screen found with auth_token. Screen ID: {screen.id}, Name: {screen.name}")
        except Screen.DoesNotExist:
            logger.warning(f"HeartbeatSerializer: No screen found with auth_token: {auth_token[:8]}...")
            raise serializers.ValidationError({'auth_token': 'Invalid authentication token'})
        except Exception as e:
            logger.error(f"HeartbeatSerializer: Error fetching screen: {str(e)}", exc_info=True)
            raise serializers.ValidationError({'auth_token': 'Error validating authentication token'})
        
        # Authenticate
        if not screen.authenticate(auth_token, secret_key):
            logger.warning(f"HeartbeatSerializer: Authentication failed for screen {screen.id}. Token matches but secret_key is incorrect.")
            raise serializers.ValidationError({'secret_key': 'Invalid secret key'})
        
        logger.info(f"HeartbeatSerializer: Authentication successful for screen {screen.id} ({screen.name})")
        attrs['screen'] = screen
        return attrs


class CommandSerializer(serializers.ModelSerializer):
    """Serializer for Command model"""
    payload_summary = serializers.CharField(read_only=True)
    is_executable = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Command
        fields = [
            'id', 'name', 'type', 'payload', 'priority', 'status',
            'expire_at', 'attempt_count', 'last_attempt_at',
            'payload_summary', 'is_executable', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'attempt_count', 'last_attempt_at', 'created_at'
        ]


class CommandPullSerializer(serializers.Serializer):
    """Serializer for command pull GET requests"""
    auth_token = serializers.CharField(required=True)
    secret_key = serializers.CharField(required=True)
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=50)
    
    def validate(self, attrs):
        """Validate authentication credentials"""
        auth_token = attrs.get('auth_token')
        secret_key = attrs.get('secret_key')
        
        try:
            screen = Screen.objects.get(auth_token=auth_token)
        except Screen.DoesNotExist:
            raise serializers.ValidationError({'auth_token': 'Invalid authentication token'})
        
        if not screen.authenticate(auth_token, secret_key):
            raise serializers.ValidationError({'secret_key': 'Invalid secret key'})
        
        attrs['screen'] = screen
        return attrs


class CommandResponseSerializer(serializers.Serializer):
    """Serializer for command execution response POST requests"""
    auth_token = serializers.CharField(required=True)
    secret_key = serializers.CharField(required=True)
    command_id = serializers.UUIDField(required=True)
    status = serializers.ChoiceField(required=True, choices=['done', 'failed'])
    response_payload = serializers.JSONField(required=False, default=dict)
    error_message = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate authentication and command"""
        auth_token = attrs.get('auth_token')
        secret_key = attrs.get('secret_key')
        command_id = attrs.get('command_id')
        
        try:
            screen = Screen.objects.get(auth_token=auth_token)
        except Screen.DoesNotExist:
            raise serializers.ValidationError({'auth_token': 'Invalid authentication token'})
        
        if not screen.authenticate(auth_token, secret_key):
            raise serializers.ValidationError({'secret_key': 'Invalid secret key'})
        
        try:
            command = Command.objects.get(id=command_id, screen=screen)
        except Command.DoesNotExist:
            raise serializers.ValidationError({'command_id': 'Command not found or does not belong to this screen'})
        
        attrs['screen'] = screen
        attrs['command'] = command
        return attrs


class ContentSyncSerializer(serializers.Serializer):
    """Serializer for content sync POST requests"""
    auth_token = serializers.CharField(required=True)
    secret_key = serializers.CharField(required=True)
    sync_type = serializers.ChoiceField(required=True, choices=['request', 'status'])
    content_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True
    )
    download_status = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    
    def validate(self, attrs):
        """Validate authentication"""
        auth_token = attrs.get('auth_token')
        secret_key = attrs.get('secret_key')
        
        try:
            screen = Screen.objects.get(auth_token=auth_token)
        except Screen.DoesNotExist:
            raise serializers.ValidationError({'auth_token': 'Invalid authentication token'})
        
        if not screen.authenticate(auth_token, secret_key):
            raise serializers.ValidationError({'secret_key': 'Invalid secret key'})
        
        attrs['screen'] = screen
        return attrs
    
    def validate_download_status(self, value):
        """Validate download status format"""
        if value:
            for item in value:
                if 'content_id' not in item:
                    raise serializers.ValidationError('Each download_status item must have content_id')
                if 'status' not in item:
                    raise serializers.ValidationError('Each download_status item must have status')
                if item['status'] not in ['success', 'failed', 'pending']:
                    raise serializers.ValidationError('Status must be one of: success, failed, pending')
        return value


class TemplateContentSerializer(serializers.ModelSerializer):
    """Serializer for Template content information"""
    class Meta:
        model = Content
        fields = [
            'id', 'name', 'type', 'file_url', 'content_json',
            'duration', 'order', 'is_active', 'download_status'
        ]


class TemplateSerializer(serializers.ModelSerializer):
    """Serializer for Template model (simplified for API)"""
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'description', 'orientation',
            'width', 'height', 'version', 'is_active'
        ]


# Player-specific serializers for complete template structure
class PlayerContentSerializer(serializers.ModelSerializer):
    """Serializer for Content in player context"""
    secure_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Content
        fields = [
            'id', 'name', 'type', 'secure_url', 'content_json',
            'duration', 'autoplay', 'order', 'file_size', 'file_hash', 'is_active'
        ]
    
    def get_secure_url(self, obj):
        """Get secure URL with appropriate expiration and make it absolute"""
        if not obj.file_url:
            return ''
        
        request = self.context.get('request')
        
        # For player, use longer expiration (24 hours)
        try:
            url = obj.get_secure_url(expiration=86400)
        except:
            url = obj.file_url or ''
        
        if not url:
            return ''
        
        # If already absolute URL, return as is
        if url.startswith('http'):
            return url
        
        # Build absolute URL using request context
        if request:
            return request.build_absolute_uri(url)
        
        # Fallback: construct absolute URL from settings
        from django.conf import settings
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        clean_url = url.lstrip('/')
        return f"{base_url.rstrip('/')}/{clean_url}"


class PlayerWidgetSerializer(serializers.ModelSerializer):
    """Serializer for Widget in player context"""
    contents = serializers.SerializerMethodField()
    
    class Meta:
        model = Widget
        fields = [
            'id', 'name', 'type',
            'font_size', 'color', 'alignment', 'autoplay',
            'x', 'y', 'width', 'height', 'z_index',
            'is_active', 'contents'
        ]
    
    def get_contents(self, obj):
        """Get active contents with request context for absolute URLs"""
        active_contents = obj.get_active_contents()
        return PlayerContentSerializer(active_contents, many=True, context=self.context).data


class PlayerLayerSerializer(serializers.ModelSerializer):
    """Serializer for Layer in player context"""
    widgets = serializers.SerializerMethodField()
    
    class Meta:
        model = Layer
        fields = [
            'id', 'name', 'x', 'y', 'width', 'height', 'z_index',
            'background_color', 'opacity', 'animation_type',
            'animation_duration', 'is_active', 'widgets'
        ]
    
    def get_widgets(self, obj):
        """Get active widgets with request context for absolute URLs"""
        active_widgets = obj.get_active_widgets()
        return PlayerWidgetSerializer(active_widgets, many=True, context=self.context).data


class PlayerTemplateSerializer(serializers.ModelSerializer):
    """Serializer for complete template structure for player"""
    layers = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'orientation', 'width', 'height',
            'version', 'config_json', 'layers'
        ]
    
    def get_layers(self, obj):
        """Get only active layers, ordered by z_index"""
        active_layers = obj.layers.filter(is_active=True).order_by('z_index', 'name')
        return PlayerLayerSerializer(active_layers, many=True, context=self.context).data


# Pairing serializers
class PairingSessionSerializer(serializers.ModelSerializer):
    """Serializer for pairing session (TV side - public)"""
    is_expired = serializers.SerializerMethodField()
    expires_in_seconds = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PairingSession
        fields = [
            'pairing_code', 'pairing_token', 'status',
            'expires_at', 'is_expired', 'expires_in_seconds',
            'qr_code_url', 'created_at'
        ]
        read_only_fields = ['pairing_code', 'pairing_token', 'status', 'expires_at', 'created_at']
    
    def get_is_expired(self, obj):
        """Check if pairing session is expired"""
        return obj.is_expired()
    
    def get_expires_in_seconds(self, obj):
        """Calculate seconds until expiration"""
        if obj.is_expired():
            return 0
        delta = obj.expires_at - timezone.now()
        return max(0, int(delta.total_seconds()))
    
    def get_qr_code_url(self, obj):
        """Generate QR code URL for pairing"""
        from django.conf import settings
        # Try to get from settings, fallback to localhost
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        # Remove trailing slash if present
        base_url = base_url.rstrip('/')
        return f"{base_url}/screens/add?token={obj.pairing_token}"


class PairingBindSerializer(serializers.Serializer):
    """Serializer for binding a pairing session to a user (Dashboard side)"""
    pairing_code = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=6,
        help_text="6-digit pairing code (alternative to pairing_token)"
    )
    pairing_token = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=255,
        help_text="Pairing token from QR code (alternative to pairing_code)"
    )
    screen_name = serializers.CharField(
        required=False,
        max_length=255,
        allow_blank=True,
        allow_null=True,
        help_text="Optional name for the screen"
    )
    
    def validate(self, attrs):
        """Validate that either pairing_code or pairing_token is provided"""
        pairing_code = attrs.get('pairing_code')
        pairing_token = attrs.get('pairing_token')
        
        # Clean up empty strings
        if pairing_code == '':
            pairing_code = None
        if pairing_token == '':
            pairing_token = None
        
        if not pairing_code and not pairing_token:
            raise serializers.ValidationError({
                'non_field_errors': ['Either pairing_code or pairing_token must be provided']
            })
        
        # Find pairing session
        try:
            if pairing_code:
                session = PairingSession.objects.get(
                    pairing_code=pairing_code,
                    status='pending'
                )
            else:
                session = PairingSession.objects.get(
                    pairing_token=pairing_token,
                    status='pending'
                )
        except PairingSession.DoesNotExist:
            raise serializers.ValidationError({
                'non_field_errors': ['Invalid or expired pairing code/token']
            })
        
        # Check if expired
        if session.is_expired():
            session.mark_expired()
            raise serializers.ValidationError({
                'non_field_errors': ['Pairing code/token has expired. Please generate a new one.']
            })
        
        # Check if already paired
        if session.status != 'pending':
            raise serializers.ValidationError({
                'non_field_errors': ['This pairing code/token has already been used']
            })
        
        attrs['session'] = session
        return attrs


class PairingStatusSerializer(serializers.Serializer):
    """Serializer for checking pairing status (TV side polling)"""
    pairing_token = serializers.CharField(required=True)
    
    def validate_pairing_token(self, value):
        """Validate pairing token and return session"""
        try:
            session = PairingSession.objects.get(pairing_token=value)
        except PairingSession.DoesNotExist:
            raise serializers.ValidationError("Invalid pairing token")
        
        # Check if expired
        if session.is_expired() and session.status == 'pending':
            session.mark_expired()
        
        return session
