"""
Signal handlers for accounts app.

This module handles automatic creation of default groups and permissions
when migrations are run.
"""
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Create default groups for roles after migrations.
    
    This signal is triggered after migrations are applied and ensures
    that default groups (Admins, Managers, Viewers) exist with appropriate
    permissions.
    """
    # Only run for accounts app
    if sender.name != 'accounts':
        return
    
    # Admin Group - Full access
    admin_group, created = Group.objects.get_or_create(name='Admins')
    if created:
        # Add all permissions to Admin group
        admin_group.permissions.set(Permission.objects.all())
        print("Created 'Admins' group with all permissions")
    
    # Manager Group - Can manage own resources
    manager_group, created = Group.objects.get_or_create(name='Managers')
    if created:
        # Add specific permissions for Managers
        manager_permissions = Permission.objects.filter(
            codename__in=[
                'add_screen', 'change_screen', 'delete_screen', 'view_screen',
                'add_template', 'change_template', 'delete_template', 'view_template',
                'add_layer', 'change_layer', 'delete_layer', 'view_layer',
                'add_widget', 'change_widget', 'delete_widget', 'view_widget',
            ]
        )
        manager_group.permissions.set(manager_permissions)
        print("Created 'Managers' group with resource management permissions")
    
    # Viewer Group - Read-only access
    viewer_group, created = Group.objects.get_or_create(name='Viewers')
    if created:
        # Add view-only permissions
        viewer_permissions = Permission.objects.filter(
            codename__in=[
                'view_screen', 'view_template', 'view_layer', 'view_widget',
            ]
        )
        viewer_group.permissions.set(viewer_permissions)
        print("Created 'Viewers' group with read-only permissions")

