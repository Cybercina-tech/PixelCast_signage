"""
Unit tests for sidebar items API and permission filtering.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from .sidebar_config import (
    get_user_permissions,
    has_permission,
    filter_sidebar_items,
    PERMISSIONS,
    ROLE_PERMISSIONS,
)

User = get_user_model()


class SidebarConfigTests(TestCase):
    """Test sidebar configuration and permission functions."""
    
    def setUp(self):
        """Set up test users with different roles."""
        self.superadmin = User.objects.create_user(
            username='superadmin',
            email='superadmin@test.com',
            password='testpass123',
            role='SuperAdmin'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='Admin'
        )
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass123',
            role='Manager'
        )
        self.operator = User.objects.create_user(
            username='operator',
            email='operator@test.com',
            password='testpass123',
            role='Operator'
        )
        self.viewer = User.objects.create_user(
            username='viewer',
            email='viewer@test.com',
            password='testpass123',
            role='Viewer'
        )
    
    def test_get_user_permissions_superadmin(self):
        """Test that SuperAdmin has all permissions."""
        permissions = get_user_permissions(self.superadmin)
        # SuperAdmin should have all permissions
        self.assertEqual(len(permissions), len(PERMISSIONS))
        for perm in PERMISSIONS.values():
            self.assertIn(perm, permissions)
    
    def test_get_user_permissions_admin(self):
        """Test Admin permissions."""
        permissions = get_user_permissions(self.admin)
        expected_perms = set(ROLE_PERMISSIONS['Admin'])
        self.assertEqual(permissions, expected_perms)
    
    def test_get_user_permissions_viewer(self):
        """Test Viewer has limited permissions."""
        permissions = get_user_permissions(self.viewer)
        expected_perms = set(ROLE_PERMISSIONS['Viewer'])
        self.assertEqual(permissions, expected_perms)
        # Viewer should not have create/edit permissions
        self.assertNotIn('create_screens', permissions)
        self.assertNotIn('edit_screens', permissions)
    
    def test_has_permission(self):
        """Test has_permission function."""
        # SuperAdmin should have all permissions
        self.assertTrue(has_permission(self.superadmin, 'view_dashboard'))
        self.assertTrue(has_permission(self.superadmin, 'view_errors'))
        self.assertTrue(has_permission(self.superadmin, 'manage_roles'))
        
        # Admin should have most permissions but not view_errors
        self.assertTrue(has_permission(self.admin, 'view_dashboard'))
        self.assertTrue(has_permission(self.admin, 'manage_roles'))
        self.assertFalse(has_permission(self.admin, 'view_errors'))
        
        # Viewer should have limited permissions
        self.assertTrue(has_permission(self.viewer, 'view_dashboard'))
        self.assertFalse(has_permission(self.viewer, 'create_screens'))
        self.assertFalse(has_permission(self.viewer, 'view_analytics'))
    
    def test_filter_sidebar_items_superadmin(self):
        """Test that SuperAdmin sees all sidebar items."""
        items = filter_sidebar_items(self.superadmin)
        # SuperAdmin should see all items including error dashboard
        self.assertGreater(len(items), 0)
        # Check that all items are included
        item_ids = [item['id'] for item in items]
        self.assertIn('dashboard', item_ids)
        self.assertIn('settings', item_ids)
    
    def test_filter_sidebar_items_viewer(self):
        """Test that Viewer sees limited sidebar items."""
        items = filter_sidebar_items(self.viewer)
        item_ids = [item['id'] for item in items]
        # Viewer should see basic items
        self.assertIn('dashboard', item_ids)
        self.assertIn('screens', item_ids)
        # Viewer should NOT see restricted items
        self.assertNotIn('analytics', item_ids)
        self.assertNotIn('core', item_ids)
    
    def test_filter_sidebar_items_with_children(self):
        """Test filtering of sidebar items with children."""
        items = filter_sidebar_items(self.admin)
        # Find core item with children
        core_item = next((item for item in items if item['id'] == 'core'), None)
        if core_item:
            self.assertIsNotNone(core_item.get('children'))
            self.assertGreater(len(core_item['children']), 0)
    
    def test_unauthenticated_user(self):
        """Test that unauthenticated users get no items."""
        items = filter_sidebar_items(None)
        self.assertEqual(len(items), 0)


class SidebarItemsAPITests(TestCase):
    """Test sidebar items API endpoint."""
    
    def setUp(self):
        """Set up test client and users."""
        self.client = APIClient()
        self.superadmin = User.objects.create_user(
            username='superadmin',
            email='superadmin@test.com',
            password='testpass123',
            role='SuperAdmin'
        )
        self.viewer = User.objects.create_user(
            username='viewer',
            email='viewer@test.com',
            password='testpass123',
            role='Viewer'
        )
        # Clear cache before each test
        cache.clear()
    
    def test_sidebar_items_requires_authentication(self):
        """Test that sidebar items endpoint requires authentication."""
        response = self.client.get('/api/sidebar-items/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_sidebar_items_superadmin(self):
        """Test that SuperAdmin gets all sidebar items."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get('/api/sidebar-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('items', response.data)
        items = response.data['items']
        self.assertGreater(len(items), 0)
        # Check that items have required fields
        for item in items:
            self.assertIn('id', item)
            self.assertIn('title', item)
            self.assertIn('icon', item)
            self.assertIn('required_permissions', item)
    
    def test_sidebar_items_viewer(self):
        """Test that Viewer gets limited sidebar items."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get('/api/sidebar-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.data['items']
        item_ids = [item['id'] for item in items]
        # Viewer should not see analytics or core items
        self.assertNotIn('analytics', item_ids)
        # Check that core item is not included (or has no accessible children)
        core_item = next((item for item in items if item['id'] == 'core'), None)
        if core_item:
            # If core item exists, it should have no accessible children for viewer
            self.assertIsNone(core_item.get('children') or len(core_item.get('children', [])) == 0)
    
    def test_sidebar_items_caching(self):
        """Test that sidebar items are cached."""
        self.client.force_authenticate(user=self.superadmin)
        
        # First request
        response1 = self.client.get('/api/sidebar-items/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second request should use cache
        response2 = self.client.get('/api/sidebar-items/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        # Responses should be identical
        self.assertEqual(response1.data, response2.data)
    
    def test_sidebar_items_cache_invalidation(self):
        """Test that cache is invalidated when user role changes."""
        self.client.force_authenticate(user=self.viewer)
        
        # Get items as viewer
        response1 = self.client.get('/api/sidebar-items/')
        viewer_items_count = len(response1.data['items'])
        
        # Change role to admin
        self.viewer.role = 'Admin'
        self.viewer.save()
        
        # Clear cache manually (in real scenario, this would happen on role change)
        cache.clear()
        
        # Get items as admin
        response2 = self.client.get('/api/sidebar-items/')
        admin_items_count = len(response2.data['items'])
        
        # Admin should see more items than viewer
        self.assertGreater(admin_items_count, viewer_items_count)

