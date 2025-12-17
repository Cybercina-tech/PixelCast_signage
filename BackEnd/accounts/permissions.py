"""
Custom permissions and permission helpers for accounts app.

This module provides helper functions and classes for role-based
access control in the Digital Signage system.
"""
from django.core.exceptions import PermissionDenied


class RolePermissions:
    """
    Helper class for role-based permission checking.
    
    Provides methods to check if a user has permission to perform
    specific actions based on their role.
    """
    
    @staticmethod
    def can_view_all(user):
        """Check if user can view all resources (Admin)"""
        return user.is_admin()
    
    @staticmethod
    def can_manage_all(user):
        """Check if user can manage all resources (Admin)"""
        return user.is_admin()
    
    @staticmethod
    def can_manage_own(user):
        """Check if user can manage their own resources (Manager or Admin)"""
        return user.is_admin() or user.is_manager()
    
    @staticmethod
    def can_view_own(user):
        """Check if user can view their own resources (all roles)"""
        return user.is_active
    
    @staticmethod
    def can_edit_resource(user, resource):
        """
        Check if user can edit a specific resource.
        
        Args:
            user: User instance
            resource: Resource instance (Screen, Template, etc.) with owner/created_by field
            
        Returns:
            bool: True if user can edit the resource
        """
        if user.is_admin():
            return True
        
        if user.is_manager():
            # Manager can edit their own resources
            if hasattr(resource, 'owner') and resource.owner == user:
                return True
            if hasattr(resource, 'created_by') and resource.created_by == user:
                return True
        
        return False
    
    @staticmethod
    def can_view_resource(user, resource):
        """
        Check if user can view a specific resource.
        
        Args:
            user: User instance
            resource: Resource instance (Screen, Template, etc.)
            
        Returns:
            bool: True if user can view the resource
        """
        if user.is_admin():
            return True
        
        # Check organization access
        if hasattr(resource, 'owner') and resource.owner:
            return user.can_access_user_resource(resource.owner)
        
        if hasattr(resource, 'created_by') and resource.created_by:
            return user.can_access_user_resource(resource.created_by)
        
        return False


def require_admin(user):
    """Decorator/function to require Admin role"""
    if not user.is_admin():
        raise PermissionDenied("Admin role required")
    return True


def require_manager_or_admin(user):
    """Decorator/function to require Manager or Admin role"""
    if not (user.is_admin() or user.is_manager()):
        raise PermissionDenied("Manager or Admin role required")
    return True


def require_active_user(user):
    """Decorator/function to require active user"""
    if not user.is_active:
        raise PermissionDenied("User account is not active")
    return True

