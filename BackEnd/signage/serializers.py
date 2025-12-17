from rest_framework import serializers
from django.utils import timezone
from .models import Screen
from commands.models import Command
from templates.models import Template, Content
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


class CommandSerializer(serializers.ModelSerializer):
    """Serializer for Command model"""
    payload_summary = serializers.CharField(source='payload_summary', read_only=True)
    is_executable = serializers.BooleanField(source='is_executable', read_only=True)
    
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
