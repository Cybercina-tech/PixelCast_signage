from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone


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
        help_text="User email address (required and unique)"
    )
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="User's full name"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[phone_validator],
        help_text="User's phone number"
    )
    
    # Role & Permissions
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Viewer', 'Viewer'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Viewer',
        help_text="User role in the system"
    )
    
    # Multi-Tenant & Organization
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text="Organization name for multi-tenant support"
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
    def is_admin(self):
        """Check if user has Admin role"""
        return self.role == 'Admin'
    
    def is_manager(self):
        """Check if user has Manager role"""
        return self.role == 'Manager'
    
    def is_viewer(self):
        """Check if user has Viewer role"""
        return self.role == 'Viewer'
    
    # Permission Helper Methods
    def has_full_access(self):
        """Check if user has full access (Admin role)"""
        return self.is_admin()
    
    def can_manage_own_resources(self):
        """Check if user can manage their own resources (Manager or Admin)"""
        return self.is_admin() or self.is_manager()
    
    def has_read_only_access(self):
        """Check if user has read-only access (Viewer role)"""
        return self.is_viewer()
    
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
        Admin can access all, Manager/Viewer can access same organization.
        """
        if self.is_admin():
            return True
        if self.organization_name and other_user.organization_name:
            return self.organization_name == other_user.organization_name
        return False
    
    # Update last_seen method
    def update_last_seen(self):
        """Update last_seen timestamp to current time"""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])
    
    # Override save to ensure email is unique and lowercase
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


# Signals are handled in accounts/signals.py
