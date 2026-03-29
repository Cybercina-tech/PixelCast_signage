from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import logging
import random
from .validators import validate_username_format, validate_phone_number, validate_organization_name

logger = logging.getLogger(__name__)


# Validators
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

email_validator = EmailValidator()


class User(AbstractUser):
    """
    Custom User model for Digital Signage System.
    
    Extends Django's AbstractUser to add role-based access control,
    organization support, and additional user information.
    """
    
    # Core Information
    email = models.EmailField(
        unique=True,
        validators=[email_validator],
        help_text="User email address (required and unique)",
        db_index=True,
    )
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="User's full name",
        db_index=True,
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        help_text="User's phone number"
    )
    
    # Role & Permissions (3-tier hierarchy)
    ROLE_CHOICES = [
        ('Developer', 'Developer'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Employee',
        help_text="User role in the system"
    )
    
    # Multi-Tenant & Organization
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        validators=[validate_organization_name],
        help_text="Organization name for multi-tenant support"
    )
    
    # Security fields
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    locked_until = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Account lockout expiration time"
    )
    
    # Email verification fields
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Whether the user's email address has been verified"
    )
    verification_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text="6-digit verification code for email verification"
    )
    verification_code_expiry = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Expiration time for the verification code"
    )
    
    # Status & Metadata
    last_seen = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time user was seen (login or heartbeat)"
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when user account was created"
    )
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined', 'username']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['organization_name', 'role']),
        ]
    
    def __str__(self):
        """Return full_name if available, otherwise username"""
        return self.full_name if self.full_name else self.username
    
    # Role Helper Methods
    def is_developer(self):
        """Top tier: full system access (god mode)."""
        return self.role == 'Developer'

    def is_superadmin(self):
        """Alias for is_developer() — backward compatible name."""
        return self.is_developer()

    def is_manager(self):
        """Staff tier: manage employees, content, screens; not system settings."""
        return self.role == 'Manager'

    def is_employee(self):
        """Operational tier: screens, schedules, media only."""
        return self.role == 'Employee'

    def is_admin(self):
        """Deprecated: old Admin role; use is_developer()."""
        return False

    def is_operator(self):
        """Deprecated: old Operator role."""
        return False

    def is_viewer(self):
        """Deprecated: old Viewer role."""
        return False

    # Permission Helper Methods
    def has_full_access(self):
        """Full access (Developer only)."""
        return self.is_developer()

    def can_manage_own_resources(self):
        """All active roles may manage permitted resources."""
        return self.is_developer() or self.is_manager() or self.is_employee()

    def has_read_only_access(self):
        """No dedicated read-only tier in 3-role model."""
        return False

    def can_execute_commands(self):
        """Developer and Manager may execute commands; not Employee."""
        return self.is_developer() or self.is_manager()

    def can_manage_templates(self):
        """Developer and Manager may manage templates."""
        return self.is_developer() or self.is_manager()

    def can_view_reports(self):
        """Analytics/reports: Developer and Manager (not system logs for Manager — use sidebar/API)."""
        return self.is_developer() or self.is_manager()

    def can_manage_employees(self):
        """Managers may manage Employee users only; Developers manage all."""
        return self.is_developer() or self.is_manager()
    
    # Property Methods for Resource Counts
    @property
    def active_screens_count(self):
        """Count of active Screens owned by this user"""
        try:
            from signage.models import Screen
            return Screen.objects.filter(owner=self, is_online=True).count()
        except ImportError:
            return 0
    
    @property
    def total_screens_count(self):
        """Total count of Screens owned by this user"""
        try:
            from signage.models import Screen
            return Screen.objects.filter(owner=self).count()
        except ImportError:
            return 0
    
    @property
    def active_templates_count(self):
        """Count of active Templates created by this user"""
        try:
            from templates.models import Template
            return Template.objects.filter(created_by=self, is_active=True).count()
        except ImportError:
            return 0
    
    @property
    def total_templates_count(self):
        """Total count of Templates created by this user"""
        try:
            from templates.models import Template
            return Template.objects.filter(created_by=self).count()
        except ImportError:
            return 0
    
    # Organization Helper Methods
    def get_organization_users(self):
        """Get all users in the same organization"""
        if not self.organization_name:
            return User.objects.none()
        return User.objects.filter(
            organization_name=self.organization_name,
            is_active=True
        )
    
    def can_access_user_resource(self, other_user):
        """
        Check if this user can access resources of another user.
        Developer can access all; others may access same organization or own resources.
        """
        if self.is_developer():
            return True
        if self.id == other_user.id:
            return True
        if self.organization_name and other_user.organization_name:
            return self.organization_name == other_user.organization_name
        return False
    
    # Update last_seen method
    def update_last_seen(self):
        """Update last_seen timestamp to current time"""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])
    
    def generate_verification_code(self):
        """Generate a 6-digit random verification code and set expiry to 10 minutes from now"""
        code = str(random.randint(100000, 999999))  # Generate 6-digit code
        self.verification_code = code
        self.verification_code_expiry = timezone.now() + timedelta(minutes=10)
        self.save(update_fields=['verification_code', 'verification_code_expiry'])
        return code
    
    def clean(self):
        """Validate model fields"""
        from django.core.exceptions import ValidationError
        
        # Validate username format
        if self.username:
            try:
                validate_username_format(self.username)
            except ValidationError as e:
                raise ValidationError({'username': e.messages})
        
        # Validate email
        if self.email:
            self.email = self.email.lower()
        
        # Validate organization name
        if self.organization_name:
            try:
                validate_organization_name(self.organization_name)
            except ValidationError as e:
                raise ValidationError({'organization_name': e.messages})
        
        super().clean()
    
    # Override save to ensure email is unique and lowercase
    def save(self, *args, **kwargs):
        # Run clean validation
        self.full_clean()
        
        if self.email:
            self.email = self.email.lower()
        if not self.username:
            self.username = self.email
        
        # Validate username format on save
        if self.username:
            try:
                validate_username_format(self.username)
            except ValidationError:
                # If username validation fails, log but don't crash (for backward compatibility)
                logger.warning(f'Username validation warning for user {self.username}')
        
        super().save(*args, **kwargs)


# Signals are handled in accounts/signals.py
