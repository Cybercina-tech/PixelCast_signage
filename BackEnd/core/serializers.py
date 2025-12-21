"""
Serializers for core models.
"""
from rest_framework import serializers
from core.models import AuditLog, SystemBackup


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
