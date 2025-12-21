from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import logging
from .models import User

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    active_screens_count = serializers.IntegerField(source='active_screens_count', read_only=True)
    total_screens_count = serializers.IntegerField(source='total_screens_count', read_only=True)
    active_templates_count = serializers.IntegerField(source='active_templates_count', read_only=True)
    total_templates_count = serializers.IntegerField(source='total_templates_count', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'phone_number',
            'role', 'role_display', 'organization_name', 'is_active',
            'is_staff', 'is_superuser', 'last_seen', 'date_joined',
            'active_screens_count', 'total_screens_count',
            'active_templates_count', 'total_templates_count',
            'password'
        ]
        read_only_fields = [
            'id', 'is_staff', 'is_superuser', 'last_seen', 'date_joined'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email is unique and properly formatted"""
        if not value:
            raise serializers.ValidationError("Email is required.")
        
        # Sanitize and normalize
        value = value.strip().lower()
        
        # Validate format
        from django.core.validators import validate_email as django_validate_email
        try:
            django_validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        
        # Check uniqueness
        if self.instance and self.instance.email == value:
            return value
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value
    
    def validate_username(self, value):
        """Validate username is unique and follows rules"""
        if not value:
            raise serializers.ValidationError("Username is required.")
        
        # Sanitize
        value = value.strip()
        
        # Validate length
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        if len(value) > 150:
            raise serializers.ValidationError("Username is too long.")
        
        # Check uniqueness
        if self.instance and self.instance.username == value:
            return value
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        
        return value
    
    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user, handling password separately"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for User list view"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role',
            'role_display', 'organization_name', 'is_active',
            'last_seen', 'date_joined'
        ]
        read_only_fields = ['id', 'last_seen', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'full_name', 'phone_number', 'role', 'organization_name'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }
    
    def validate_password(self, value):
        """Enhanced password validation"""
        if not value:
            raise serializers.ValidationError("Password is required.")
        
        # Additional strength check
        from .security import PasswordStrengthChecker
        strength = PasswordStrengthChecker.check_password_strength(value)
        
        if not strength['is_strong']:
            # Provide feedback but don't block (Django validators will catch critical issues)
            if strength['feedback']:
                logger.warning(f'Weak password detected: {strength["feedback"]}')
        
        return value
    
    def validate(self, attrs):
        """Validate password confirmation and strength"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        
        # Check password strength
        from .security import PasswordStrengthChecker
        strength = PasswordStrengthChecker.check_password_strength(password)
        
        if strength['score'] < 2:
            raise serializers.ValidationError({
                "password": f"Password is too weak. {', '.join(strength['feedback'][:2])}"
            })
        
        return attrs
    
    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with security enhancements"""
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate_username(self, value):
        """Validate and sanitize username"""
        if not value:
            raise serializers.ValidationError('Username is required.')
        
        # Limit length to prevent DoS
        if len(value) > 150:
            raise serializers.ValidationError('Username is too long.')
        
        return value.strip().lower()
    
    def validate(self, attrs):
        """Validate credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError('Must include "username" and "password".')
        
        # Try username first, then email
        user = None
        try:
            user = authenticate(username=username, password=password)
        except Exception:
            pass
        
        # If username auth failed, try email
        if not user:
            try:
                from .models import User
                user_obj = User.objects.get(email=username.lower())
                user = authenticate(username=user_obj.username, password=password)
            except (User.DoesNotExist, Exception):
                pass
        
        if not user:
            # Don't reveal whether user exists (prevent enumeration)
            raise serializers.ValidationError('Unable to log in with provided credentials.')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        
        attrs['user'] = user
        return attrs


class RoleSerializer(serializers.Serializer):
    """Serializer for role management"""
    ROLE_CHOICES = [
        ('SuperAdmin', 'Super Admin'),
        ('Admin', 'Admin'),
        ('Operator', 'Operator'),
        ('Manager', 'Manager'),
        ('Viewer', 'Viewer'),
    ]
    
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    description = serializers.CharField(read_only=True)
    
    def get_description(self, role):
        """Get role description"""
        descriptions = {
            'SuperAdmin': 'Full system access with all permissions',
            'Admin': 'Administrative access to manage users and resources',
            'Operator': 'Can execute commands and manage resources',
            'Manager': 'Can manage own resources and view reports',
            'Viewer': 'Read-only access to view resources',
        }
        return descriptions.get(role, '')


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        if not value:
            raise serializers.ValidationError("New password is required.")
        
        # Check password strength
        from .security import PasswordStrengthChecker
        strength = PasswordStrengthChecker.check_password_strength(value)
        
        if strength['score'] < 2:
            raise serializers.ValidationError(
                f"Password is too weak. {', '.join(strength['feedback'][:2])}"
            )
        
        return value
    
    def validate(self, attrs):
        """Validate password change"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({"new_password_confirm": "Password fields didn't match."})
        
        # Ensure new password is different from old password
        old_password = attrs.get('old_password')
        if old_password and new_password == old_password:
            raise serializers.ValidationError({"new_password": "New password must be different from old password."})
        
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        if not value:
            raise serializers.ValidationError("Old password is required.")
        
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        
        return value
