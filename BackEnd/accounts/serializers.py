from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User


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
        """Validate email is unique"""
        if self.instance and self.instance.email == value:
            return value
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_username(self, value):
        """Validate username is unique"""
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
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
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
    """Serializer for user login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include "username" and "password".')
        
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
    
    def validate(self, attrs):
        """Validate password change"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Password fields didn't match."})
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
