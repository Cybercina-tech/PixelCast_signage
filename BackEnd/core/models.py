"""
Core models for audit logging and system tracking.
"""
import uuid
import json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class AuditLog(models.Model):
    """
    Comprehensive audit log for tracking all critical system actions.

    Tracks:
    - CRUD operations on all models
    - Command executions
    - Template activations
    - Schedule changes
    - Authentication events
    - Permission changes
    - Bulk operations
    """

    ACTION_TYPES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
        ('execute', 'Execute'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('role_change', 'Role Change'),
        ('bulk_operation', 'Bulk Operation'),
        ('backup', 'Backup'),
        ('restore', 'Restore'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('other', 'Other'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the audit log entry"
    )

    # User and session info
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    username = models.CharField(
        max_length=150,
        blank=True,
        help_text="Username at time of action (for historical accuracy)"
    )
    user_role = models.CharField(
        max_length=50,
        blank=True,
        help_text="User role at time of action"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the client"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string"
    )

    # Action details
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPES,
        help_text="Type of action performed"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default='medium',
        help_text="Severity level of the action"
    )

    # Resource information (Generic Foreign Key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Content type of the affected resource"
    )
    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID of the affected resource"
    )
    resource = GenericForeignKey('content_type', 'object_id')

    # Resource details
    resource_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Type of resource (e.g., 'Screen', 'Template')"
    )
    resource_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name or identifier of the resource"
    )

    # Action details
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of the action"
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON object describing what changed (before/after)"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the action"
    )

    # Result
    success = models.BooleanField(
        default=True,
        help_text="Whether the action was successful"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if action failed"
    )

    # Timestamp
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the action occurred"
    )

    class Meta:
        db_table = 'core_audit_log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['resource_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        """Return string representation."""
        user_str = self.username or 'Anonymous'
        action_str = self.get_action_type_display()
        resource_str = self.resource_name or self.resource_type or 'Unknown'
        return f"{user_str} {action_str} {resource_str} at {self.timestamp}"

    def get_changes_summary(self) -> str:
        """Get a summary of changes made."""
        if not self.changes:
            return "No changes recorded"

        before = self.changes.get('before', {})
        after = self.changes.get('after', {})

        if not before and not after:
            return "No changes recorded"

        summary_parts = []
        for key in set(list(before.keys()) + list(after.keys())):
            old_value = before.get(key, 'N/A')
            new_value = after.get(key, 'N/A')
            if old_value != new_value:
                summary_parts.append(f"{key}: {old_value} → {new_value}")

        return "; ".join(summary_parts) if summary_parts else "No changes recorded"


class SystemBackup(models.Model):
    """
    Tracks automated and manual backups of the system.
    """

    BACKUP_TYPES = [
        ('database', 'Database'),
        ('media', 'Media Files'),
        ('full', 'Full System'),
        ('incremental', 'Incremental'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the backup"
    )

    backup_type = models.CharField(
        max_length=20,
        choices=BACKUP_TYPES,
        help_text="Type of backup"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the backup"
    )

    # Backup metadata
    file_path = models.CharField(
        max_length=1000,
        blank=True,
        help_text="Path to backup file (local or cloud)"
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Size of backup file in bytes"
    )
    checksum = models.CharField(
        max_length=128,
        blank=True,
        help_text="Checksum/hash of backup file for integrity verification"
    )

    # Configuration
    include_media = models.BooleanField(
        default=False,
        help_text="Whether media files are included"
    )
    compression = models.BooleanField(
        default=True,
        help_text="Whether backup is compressed"
    )
    encryption = models.BooleanField(
        default=False,
        help_text="Whether backup is encrypted"
    )

    # Scheduling
    scheduled = models.BooleanField(
        default=False,
        help_text="Whether this was an automated scheduled backup"
    )
    schedule_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the schedule if scheduled"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional backup metadata"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if backup failed"
    )

    # User info
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_backups',
        help_text="User who triggered the backup"
    )

    # Timestamps
    started_at = models.DateTimeField(
        default=timezone.now,
        help_text="When backup started"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When backup completed"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When backup expires (for retention policy)"
    )

    class Meta:
        db_table = 'core_system_backup'
        verbose_name = 'System Backup'
        verbose_name_plural = 'System Backups'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['backup_type', 'started_at']),
            models.Index(fields=['scheduled', 'started_at']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        """Return string representation."""
        return f"{self.get_backup_type_display()} backup - {self.get_status_display()} ({self.started_at})"

    @property
    def duration(self):
        """Calculate backup duration."""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None

    def is_expired(self) -> bool:
        """Check if backup has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
