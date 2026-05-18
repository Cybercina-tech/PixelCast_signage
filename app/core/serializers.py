"""
Serializers for core models.
"""
from rest_framework import serializers
from core.models import (
    AuditLog,
    SystemBackup,
    Notification,
    NotificationPreference,
    SystemEmailSettings,
)


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    username = serializers.CharField(read_only=True)
    resource_type = serializers.CharField(read_only=True)
    resource_name = serializers.CharField(read_only=True)
    changes_summary = serializers.CharField(source='get_changes_summary', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'username',
            'user_role',
            'ip_address',
            'action_type',
            'action_type_display',
            'severity',
            'severity_display',
            'resource_type',
            'resource_name',
            'description',
            'changes',
            'changes_summary',
            'metadata',
            'success',
            'error_message',
            'timestamp',
        ]
        read_only_fields = fields


class SystemBackupSerializer(serializers.ModelSerializer):
    """Serializer for SystemBackup model."""
    backup_type_display = serializers.CharField(source='get_backup_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = SystemBackup
        fields = [
            'id',
            'backup_type',
            'backup_type_display',
            'status',
            'status_display',
            'file_path',
            'file_size',
            'file_size_mb',
            'checksum',
            'include_media',
            'compression',
            'encryption',
            'scheduled',
            'schedule_name',
            'metadata',
            'error_message',
            'created_by',
            'created_by_username',
            'started_at',
            'completed_at',
            'expires_at',
            'duration_seconds',
        ]
        read_only_fields = [
            'id',
            'status',
            'file_path',
            'file_size',
            'checksum',
            'error_message',
            'started_at',
            'completed_at',
        ]

    def get_duration_seconds(self, obj):
        """Get backup duration in seconds."""
        duration = obj.duration
        return duration.total_seconds() if duration else None

    def get_file_size_mb(self, obj):
        """Get file size in MB."""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'type',
            'type_display',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user notification preferences."""

    class Meta:
        model = NotificationPreference
        fields = [
            'screen_offline',
            'template_push',
            'system_updates',
            'email_enabled',
            'notification_email',
            'updated_at',
        ]
        read_only_fields = ['updated_at']


class SystemEmailSettingsSerializer(serializers.ModelSerializer):
    """Read/update system SMTP; password is write-only and never returned."""

    smtp_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    smtp_password_configured = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SystemEmailSettings
        fields = [
            'delivery_mode',
            'smtp_host',
            'smtp_port',
            'use_tls',
            'use_ssl',
            'smtp_username',
            'smtp_password',
            'smtp_password_configured',
            'default_from_email',
            'last_smtp_test_at',
            'last_smtp_test_ok',
            'last_smtp_test_error_code',
            'last_smtp_test_detail',
            'updated_at',
            'created_at',
        ]
        read_only_fields = [
            'updated_at',
            'created_at',
            'smtp_password_configured',
            'last_smtp_test_at',
            'last_smtp_test_ok',
            'last_smtp_test_error_code',
            'last_smtp_test_detail',
        ]

    def get_smtp_password_configured(self, obj):
        return bool((obj.smtp_password_encrypted or '').strip())

    def validate(self, attrs):
        delivery = attrs.get('delivery_mode', getattr(self.instance, 'delivery_mode', None))
        use_tls = attrs.get('use_tls', getattr(self.instance, 'use_tls', True))
        use_ssl = attrs.get('use_ssl', getattr(self.instance, 'use_ssl', False))
        if use_tls and use_ssl:
            raise serializers.ValidationError(
                {'use_tls': 'Enable only one of TLS (STARTTLS) or SSL (implicit TLS), not both.'}
            )
        host = (attrs.get('smtp_host') or getattr(self.instance, 'smtp_host', '') or '').strip()
        port = attrs.get('smtp_port', getattr(self.instance, 'smtp_port', 587))
        if delivery == SystemEmailSettings.DELIVERY_SMTP:
            if not host:
                raise serializers.ValidationError({'smtp_host': 'SMTP host is required when using SMTP delivery.'})
            try:
                p = int(port)
            except (TypeError, ValueError):
                raise serializers.ValidationError({'smtp_port': 'Invalid port.'})
            if p < 1 or p > 65535:
                raise serializers.ValidationError({'smtp_port': 'Port must be between 1 and 65535.'})
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('smtp_password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            if str(password).strip():
                instance.set_smtp_password(password)
            else:
                instance.clear_smtp_password()
        instance.save()
        return instance


class SystemEmailTestSerializer(serializers.Serializer):
    to = serializers.EmailField()
