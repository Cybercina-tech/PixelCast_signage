import uuid
import json
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


def default_command_payload():
    """Return an empty dict for command payload default values."""
    return {}


class Command(models.Model):
    """
    Digital Signage Command model for managing immediate commands sent to Screens.
    
    Commands are instructions that can be sent to screens for immediate execution,
    such as restart, refresh, change template, or display messages. Commands are
    queued and executed when the screen is online, with retry logic and priority support.
    """
    
    # Core Information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the command"
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional description or name for the command"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this command was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this command was last updated"
    )
    
    # Relations
    screen = models.ForeignKey(
        'signage.Screen',
        on_delete=models.CASCADE,
        related_name='commands',
        help_text="Screen that should execute this command"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_commands',
        help_text="User who created/sent this command"
    )
    
    # Command Type & Payload
    COMMAND_TYPE_CHOICES = [
        ('restart', 'Restart'),
        ('refresh', 'Refresh'),
        ('change_template', 'Change Template'),
        ('display_message', 'Display Message'),
        ('custom', 'Custom'),
    ]
    type = models.CharField(
        max_length=50,
        choices=COMMAND_TYPE_CHOICES,
        help_text="Type of command to execute"
    )
    payload = models.JSONField(
        default=default_command_payload,
        blank=True,
        help_text="Additional parameters for command execution (JSON format)"
    )
    priority = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Priority level (higher number = higher priority)"
    )
    expire_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Command expires after this time (optional)"
    )
    
    # Status Tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the command"
    )
    last_attempt_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time command execution was attempted"
    )
    attempt_count = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of times execution was attempted"
    )
    
    class Meta:
        db_table = 'commands_command'
        verbose_name = 'Command'
        verbose_name_plural = 'Commands'
        ordering = ['-priority', 'created_at']
        indexes = [
            models.Index(fields=['screen', 'status']),
            models.Index(fields=['screen', 'priority', 'status']),
            models.Index(fields=['type', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['expire_at', 'status']),
        ]
    
    def __str__(self):
        """Return string representation: '{screen name} - {type} ({status})'"""
        status_display = self.get_status_display()
        return f"{self.screen.name} - {self.get_type_display()} ({status_display})"
    
    def clean(self):
        """Validate command data"""
        super().clean()
        
        # Validate payload based on command type
        if self.payload:
            try:
                # Ensure payload is valid JSON
                json.dumps(self.payload)
            except (TypeError, ValueError):
                raise ValidationError({
                    'payload': 'Payload must be valid JSON'
                })
            
            # Type-specific validation
            if self.type == 'change_template' and 'template_id' not in self.payload:
                raise ValidationError({
                    'payload': 'change_template command requires template_id in payload'
                })
            
            if self.type == 'display_message' and 'message' not in self.payload:
                raise ValidationError({
                    'payload': 'display_message command requires message in payload'
                })
        
        # Validate expire_at is in the future if set
        if self.expire_at and self.expire_at <= timezone.now():
            raise ValidationError({
                'expire_at': 'Expiration time must be in the future'
            })
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    # Status Management Methods
    def mark_done(self):
        """Mark command as successfully executed"""
        self.status = 'done'
        self.last_attempt_at = timezone.now()
        self.save(update_fields=['status', 'last_attempt_at'])
    
    def mark_failed(self):
        """Mark command execution as failed"""
        self.status = 'failed'
        self.attempt_count += 1
        self.last_attempt_at = timezone.now()
        self.save(update_fields=['status', 'attempt_count', 'last_attempt_at'])
    
    def reset_status(self):
        """Reset command status to pending (for retry)"""
        self.status = 'pending'
        self.last_attempt_at = None
        self.save(update_fields=['status', 'last_attempt_at'])
    
    # Operational Methods
    def is_expired(self):
        """Check if command has expired"""
        if not self.expire_at:
            return False
        return timezone.now() > self.expire_at
    
    def can_retry(self, max_retries=3):
        """
        Check if command can be retried.
        
        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            bool: True if command can be retried, False otherwise
        """
        # Cannot retry if already done
        if self.status == 'done':
            return False
        
        # Cannot retry if expired
        if self.is_expired():
            return False
        
        # Cannot retry if exceeded max attempts
        if self.attempt_count >= max_retries:
            return False
        
        return True
    
    def execute_command(self):
        """
        Execute the command on the target screen.
        
        This is a placeholder method that should be implemented with actual
        command execution logic. In production, this would:
        1. Check if screen is online
        2. Send command via screen's API
        3. Wait for acknowledgment
        4. Update status accordingly
        
        Returns:
            bool: True if execution successful, False otherwise
        """
        # Check if command is expired
        if self.is_expired():
            self.status = 'failed'
            self.save(update_fields=['status'])
            return False
        
        # Check if screen is online
        if not self.screen.is_online:
            # Screen is offline, keep command as pending
            return False
        
        # Update attempt tracking
        self.attempt_count += 1
        self.last_attempt_at = timezone.now()
        
        try:
            # Execute command based on type
            success = self._execute_by_type()
            
            if success:
                self.mark_done()
                return True
            else:
                self.mark_failed()
                return False
                
        except Exception as e:
            # Log error (in production, use proper logging)
            print(f"Error executing command {self.id}: {str(e)}")
            self.mark_failed()
            return False
    
    def _execute_by_type(self):
        """
        Execute command based on its type.
        
        This is a helper method that handles execution logic for each command type.
        In production, this would integrate with screen's API or communication protocol.
        
        Returns:
            bool: True if execution successful, False otherwise
        """
        if self.type == 'restart':
            # Send restart command to screen
            # In production: screen.restart() or API call
            return self._send_to_screen('restart', {})
        
        elif self.type == 'refresh':
            # Send refresh command to screen
            return self._send_to_screen('refresh', {})
        
        elif self.type == 'change_template':
            # Change active template on screen
            template_id = self.payload.get('template_id')
            if not template_id:
                return False
            return self._send_to_screen('change_template', {'template_id': template_id})
        
        elif self.type == 'display_message':
            # Display message on screen
            message = self.payload.get('message')
            if not message:
                return False
            return self._send_to_screen('display_message', {'message': message})
        
        elif self.type == 'custom':
            # Execute custom command with payload
            return self._send_to_screen('custom', self.payload)
        
        return False
    
    def _send_to_screen(self, command_type, data):
        """
        Send command to screen via API or communication protocol.
        
        This is a placeholder method. In production, this would:
        1. Use screen's API endpoint
        2. Use WebSocket connection
        3. Use MQTT or other messaging protocol
        4. Handle authentication and encryption
        
        Args:
            command_type: Type of command to send
            data: Command data/payload
            
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        # Placeholder implementation
        # In production, this would use actual communication with screen
        
        # For now, simulate successful send if screen is online
        if self.screen.is_online:
            # Update screen's last_command_sent_at
            self.screen.last_command_sent_at = timezone.now()
            self.screen.save(update_fields=['last_command_sent_at'])
            return True
        
        return False
    
    # Property Methods
    @property
    def is_pending(self):
        """Check if command is pending execution"""
        return self.status == 'pending' and not self.is_expired()
    
    @property
    def is_executable(self):
        """Check if command can be executed now"""
        return (
            self.is_pending and
            self.screen.is_online and
            not self.is_expired()
        )
    
    @property
    def time_until_expiry(self):
        """Calculate time remaining until expiry (in seconds)"""
        if not self.expire_at:
            return None
        delta = self.expire_at - timezone.now()
        return max(0, delta.total_seconds())
    
    @property
    def payload_summary(self):
        """Get a summary of payload for display"""
        if not self.payload:
            return "No payload"
        
        # Create a readable summary
        if self.type == 'change_template':
            return f"Template ID: {self.payload.get('template_id', 'N/A')}"
        elif self.type == 'display_message':
            message = self.payload.get('message', '')
            return f"Message: {message[:50]}..." if len(message) > 50 else f"Message: {message}"
        elif self.type == 'custom':
            return f"Custom data: {len(self.payload)} fields"
        else:
            return "Standard command"
