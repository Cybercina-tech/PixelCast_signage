from rest_framework import serializers
from django.utils import timezone
from .models import Template, Layer, Widget, Content, Schedule
from accounts.permissions import RolePermissions


class ContentSerializer(serializers.ModelSerializer):
    """Serializer for Content model"""
    is_downloaded = serializers.BooleanField(read_only=True)
    needs_download = serializers.BooleanField(read_only=True)
    file_extension = serializers.CharField(read_only=True)
    is_media_file = serializers.BooleanField(read_only=True)
    estimated_size_mb = serializers.FloatField(read_only=True)
    absolute_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Content
        fields = [
            'id', 'name', 'description', 'type', 'file_url', 'absolute_file_url', 'content_json',
            'text_content', 'duration', 'autoplay', 'order', 'widget', 'is_active',
            'downloaded', 'download_status', 'last_download_attempt',
            'retry_count', 'is_downloaded', 'needs_download', 'file_extension',
            'is_media_file', 'estimated_size_mb', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'downloaded', 'download_status', 'last_download_attempt',
            'retry_count', 'created_at', 'updated_at'
        ]
    
    def get_absolute_file_url(self, obj):
        """Return absolute URL for the file"""
        if not obj.file_url:
            return None
        
        request = self.context.get('request')
        if request:
            # Use request to build absolute URL
            if obj.file_url.startswith('http'):
                return obj.file_url
            return request.build_absolute_uri(obj.file_url)
        
        # Fallback if no request context
        if obj.file_url.startswith('http'):
            return obj.file_url
        
        # Use settings to construct URL
        from django.conf import settings
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        if obj.file_url.startswith(media_url):
            return obj.file_url
        
        # Construct full URL
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        clean_url = obj.file_url.lstrip('/')
        clean_media = media_url.rstrip('/').lstrip('/')
        return f"{base_url.rstrip('/')}/{clean_media}/{clean_url}"


class WidgetSerializer(serializers.ModelSerializer):
    """Serializer for Widget model"""
    contents = ContentSerializer(many=True, read_only=True)
    active_contents_count = serializers.SerializerMethodField()
    total_contents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Widget
        fields = [
            'id', 'name', 'type', 'content_url', 'content_json',
            'font_size', 'color', 'alignment', 'autoplay',
            'x', 'y', 'width', 'height', 'z_index', 'layer',
            'is_active', 'contents', 'active_contents_count',
            'total_contents_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_contents_count(self, obj):
        """Get count of active contents"""
        return obj.get_active_contents().count()
    
    def get_total_contents_count(self, obj):
        """Get total count of contents"""
        return obj.get_contents_count()


class LayerSerializer(serializers.ModelSerializer):
    """Serializer for Layer model"""
    widgets = WidgetSerializer(many=True, read_only=True)
    active_widgets_count = serializers.SerializerMethodField()
    total_widgets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Layer
        fields = [
            'id', 'name', 'description', 'x', 'y', 'width', 'height',
            'z_index', 'background_color', 'opacity', 'animation_type',
            'animation_duration', 'template', 'is_active', 'widgets',
            'active_widgets_count', 'total_widgets_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_widgets_count(self, obj):
        """Get count of active widgets"""
        return obj.get_active_widgets().count()
    
    def get_total_widgets_count(self, obj):
        """Get total count of widgets"""
        return obj.get_widgets().count()


class TemplateSerializer(serializers.ModelSerializer):
    """Serializer for Template model"""
    layers = LayerSerializer(many=True, read_only=True)
    layers_count = serializers.SerializerMethodField()
    widgets_count = serializers.SerializerMethodField()
    contents_count = serializers.SerializerMethodField()
    screens_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'description', 'orientation', 'width', 'height',
            'thumbnail', 'created_by', 'is_active', 'version', 'config_json',
            'meta_data', 'layers', 'layers_count', 'widgets_count',
            'contents_count', 'screens_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'orientation': {'required': False},  # Has default
            'width': {'required': False},  # Has default
            'height': {'required': False},  # Has default
            'is_active': {'required': False},  # Has default
        }
    
    def validate_name(self, value):
        """Validate template name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Template name is required and cannot be empty.")
        if len(value.strip()) > 255:
            raise serializers.ValidationError("Template name cannot exceed 255 characters.")
        return value.strip()
    
    def validate_width(self, value):
        """Validate template width"""
        if value is not None and value < 1:
            raise serializers.ValidationError("Width must be at least 1 pixel.")
        return value
    
    def validate_height(self, value):
        """Validate template height"""
        if value is not None and value < 1:
            raise serializers.ValidationError("Height must be at least 1 pixel.")
        return value
    
    def validate(self, attrs):
        """Validate template data"""
        # Ensure name is provided
        if not attrs.get('name'):
            raise serializers.ValidationError({
                'name': 'Template name is required.'
            })
        
        return attrs
    
    def get_layers_count(self, obj):
        """Get count of layers"""
        return obj.get_layers().count()
    
    def get_widgets_count(self, obj):
        """Get count of widgets"""
        return obj.get_widgets().count()
    
    def get_contents_count(self, obj):
        """Get count of contents"""
        return obj.get_all_contents().count()
    
    def get_screens_count(self, obj):
        """Get count of screens"""
        return obj.screens.count()


class TemplateListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Template list view"""
    layers_count = serializers.SerializerMethodField()
    screens_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'description', 'orientation', 'width', 'height',
            'thumbnail', 'is_active', 'version', 'layers_count',
            'screens_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_layers_count(self, obj):
        return obj.get_layers().count()
    
    def get_screens_count(self, obj):
        return obj.screens.count()


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Schedule model"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_id = serializers.UUIDField(source='template.id', read_only=True)
    screens_count = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()
    is_running_now = serializers.SerializerMethodField()
    next_run = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'name', 'description', 'template', 'template_id', 'template_name',
            'start_time', 'end_time', 'is_active', 'repeat_type', 'priority',
            'last_executed_at', 'is_currently_running', 'screens_count',
            'duration', 'is_past', 'is_running_now', 'next_run',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_executed_at', 'is_currently_running',
            'created_at', 'updated_at'
        ]
    
    def get_screens_count(self, obj):
        """Get count of screens assigned to this schedule"""
        return obj.screens_count
    
    def get_duration(self, obj):
        """Get duration of the schedule"""
        return obj.duration
    
    def get_is_past(self, obj):
        """Check if schedule is in the past"""
        return obj.is_past
    
    def get_is_running_now(self, obj):
        """Check if schedule is currently running"""
        return obj.is_running_now
    
    def get_screens_count(self, obj):
        """Get count of screens assigned to this schedule"""
        return obj.screens_count
    
    def get_duration(self, obj):
        """Get duration of the schedule"""
        return obj.duration
    
    def get_is_past(self, obj):
        """Check if schedule is in the past"""
        return obj.is_past
    
    def get_is_running_now(self, obj):
        """Check if schedule is currently running"""
        return obj.is_running_now
    
    def get_next_run(self, obj):
        """Get next run time"""
        next_run = obj.next_run()
        return next_run.isoformat() if next_run else None
    
    def validate(self, attrs):
        """Validate schedule data"""
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time.'
                })
        
        return attrs


class ScheduleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Schedule list view"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    screens_count = serializers.SerializerMethodField()
    is_running_now = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'name', 'description', 'template', 'template_name',
            'start_time', 'end_time', 'is_active', 'repeat_type', 'priority',
            'is_currently_running', 'screens_count', 'is_running_now',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_screens_count(self, obj):
        """Get count of screens assigned to this schedule"""
        return obj.screens_count
    
    def get_is_running_now(self, obj):
        """Check if schedule is currently running"""
        return obj.is_running_now


class TemplateActivationSerializer(serializers.Serializer):
    """Serializer for template activation on screen"""
    screen_id = serializers.UUIDField(required=True)
    sync_content = serializers.BooleanField(default=True)
    
    def validate_screen_id(self, value):
        """Validate screen exists"""
        from signage.models import Screen
        try:
            screen = Screen.objects.get(id=value)
        except Screen.DoesNotExist:
            raise serializers.ValidationError('Screen not found')
        return value


class ScheduleExecutionSerializer(serializers.Serializer):
    """Serializer for schedule execution"""
    force = serializers.BooleanField(default=False, help_text='Force execution even if not due')
    
    def validate(self, attrs):
        """Validate schedule can be executed"""
        schedule = self.instance
        if not schedule:
            raise serializers.ValidationError('Schedule instance required')
        
        if not schedule.is_active:
            raise serializers.ValidationError('Schedule is not active')
        
        if not schedule.screens.exists():
            raise serializers.ValidationError('No screens assigned to this schedule')
        
        return attrs
