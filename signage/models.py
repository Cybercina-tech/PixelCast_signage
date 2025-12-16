import uuid
import secrets
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Screen(models.Model):
    """
    Digital Signage Screen model for managing display devices.
    
    This model tracks all aspects of a digital signage screen including
    device information, status, security, technical specifications, and logs.
    """
    
    # Core Information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the screen"
    )
    name = models.CharField(
        max_length=255,
        help_text="Display name for the screen"
    )
    device_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique device identifier"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Physical location of the screen"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Additional description or notes about the screen"
    )
    
    # Relations
    active_template = models.ForeignKey(
        'templates.Template',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_screens',
        help_text="Currently active template assigned to this screen"
    )
    assigned_schedules = models.ManyToManyField(
        'signage.Schedule',
        blank=True,
        related_name='screens',
        help_text="Schedules assigned to this screen"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_screens',
        help_text="User who owns or manages this screen"
    )
    
    # System & Security
    auth_token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        blank=True,
        help_text="Authentication token for device communication (auto-generated if not provided)"
    )
    secret_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        blank=True,
        help_text="Secret key for secure device operations (auto-generated if not provided)"
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the screen was registered"
    )
    last_ip = models.GenericIPAddressField(
        protocol='both',
        unpack_ipv4=False,
        blank=True,
        null=True,
        help_text="Last known IP address of the device"
    )
    
    # Status Tracking
    is_online = models.BooleanField(
        default=False,
        help_text="Whether the screen is currently online"
    )
    last_heartbeat_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time a heartbeat was received from the device"
    )
    last_command_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time a command was sent to the device"
    )
    last_command_received_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time a command response was received from the device"
    )
    last_template_update_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time the template was updated on the device"
    )
    is_busy = models.BooleanField(
        default=False,
        help_text="Whether the screen is currently processing a command"
    )
    
    # Technical Info
    app_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Version of the signage application running on the device"
    )
    os_version = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Operating system version of the device"
    )
    device_model = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Model name/number of the device"
    )
    screen_width = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Screen width in pixels"
    )
    screen_height = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Screen height in pixels"
    )
    brightness = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Screen brightness level (0-100)"
    )
    ORIENTATION_CHOICES = [
        ('landscape', 'Landscape'),
        ('portrait', 'Portrait'),
        ('reverse_landscape', 'Reverse Landscape'),
        ('reverse_portrait', 'Reverse Portrait'),
    ]
    orientation = models.CharField(
        max_length=20,
        choices=ORIENTATION_CHOICES,
        default='landscape',
        help_text="Screen orientation"
    )
    
    # Inline Logs
    last_error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Last error message received from the device"
    )
    last_sync_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Last synchronization status"
    )
    last_download_error = models.TextField(
        blank=True,
        null=True,
        help_text="Last download error message"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )
    
    class Meta:
        db_table = 'signage_screen'
        verbose_name = 'Screen'
        verbose_name_plural = 'Screens'
        ordering = ['-registration_date', 'name']
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['auth_token']),
            models.Index(fields=['is_online', 'last_heartbeat_at']),
            models.Index(fields=['owner', 'is_online']),
        ]
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate auth_token and secret_key if not provided."""
        if not self.auth_token:
            self.auth_token = secrets.token_urlsafe(32)
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def is_heartbeat_stale(self, timeout_minutes=5):
        """
        Check if the last heartbeat is stale (older than timeout_minutes).
        
        Args:
            timeout_minutes: Number of minutes to consider a heartbeat stale
            
        Returns:
            bool: True if heartbeat is stale or missing, False otherwise
        """
        if not self.last_heartbeat_at:
            return True
        from django.utils import timezone
        from datetime import timedelta
        threshold = timezone.now() - timedelta(minutes=timeout_minutes)
        return self.last_heartbeat_at < threshold


class Schedule(models.Model):
    """Schedule model for content scheduling."""
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'signage_schedule'
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
    
    def __str__(self):
        return self.name
