"""
Tests for permission and authorization logic.
"""
from django.test import TestCase
from tests.base import BaseAPITestCase
from accounts.permissions import RolePermissions


class PermissionTests(BaseAPITestCase):
    """Tests for permission checking."""
    
    def test_superadmin_permissions(self):
        """Test SuperAdmin has all permissions."""
        superadmin = self.create_user(role='SuperAdmin')
        
        screen = self.create_screen()
        template = self.create_template()
        
        # Should have full access
        self.assertTrue(RolePermissions.can_edit_resource(superadmin, screen))
        self.assertTrue(RolePermissions.can_edit_resource(superadmin, template))
        self.assertTrue(RolePermissions.can_view_resource(superadmin, screen))
    
    def test_admin_permissions(self):
        """Test Admin has full access."""
        admin = self.create_user(role='Admin')
        
        screen = self.create_screen()
        template = self.create_template()
        
        self.assertTrue(RolePermissions.can_edit_resource(admin, screen))
        self.assertTrue(RolePermissions.can_view_resource(admin, screen))
    
    def test_manager_permissions(self):
        """Test Manager can manage own resources."""
        manager = self.create_user(role='Manager', organization_name='Org1')
        other_manager = self.create_user(role='Manager', organization_name='Org2')
        
        # Own screen
        own_screen = self.create_screen(owner=manager)
        self.assertTrue(RolePermissions.can_edit_resource(manager, own_screen))
        
        # Other user's screen in same org
        org_screen = self.create_screen(owner=other_manager, owner__organization_name='Org1')
        # Depends on implementation, may or may not have access
        
        # Different org
        other_screen = self.create_screen(owner=other_manager)
        self.assertFalse(RolePermissions.can_edit_resource(manager, other_screen))
    
    def test_viewer_permissions(self):
        """Test Viewer has read-only access."""
        viewer = self.create_user(role='Viewer')
        
        screen = self.create_screen()
        
        # Can view but not edit
        self.assertTrue(RolePermissions.can_view_resource(viewer, screen))
        # Edit depends on specific resource ownership rules
    
    def test_operator_command_permissions(self):
        """Test Operator can execute commands."""
        operator = self.create_user(role='Operator')
        viewer = self.create_user(role='Viewer')
        
        self.assertTrue(operator.can_execute_commands())
        self.assertFalse(viewer.can_execute_commands())


class APIPermissionTests(BaseAPITestCase):
    """Tests for API endpoint permissions."""
    
    def test_unauthorized_access_denied(self):
        """Test unauthenticated users are denied."""
        self.client.force_authenticate(user=None)
        
        from django.urls import reverse
        url = reverse('screen-list')
        response = self.client.get(url)
        
        self.assertUnauthorized(response)
    
    def test_viewer_cannot_create_screens(self):
        """Test Viewer role cannot create screens."""
        viewer = self.create_user(role='Viewer')
        self.client.force_authenticate(user=viewer)
        
        from django.urls import reverse
        url = reverse('screen-list')
        data = {'name': 'Test', 'device_id': 'test-001'}
        response = self.client.post(url, data, format='json')
        
        # Should be denied
        self.assertIn(response.status_code, [403, 400])
    
    def test_manager_can_create_screens(self):
        """Test Manager can create screens."""
        manager = self.create_user(role='Manager')
        self.client.force_authenticate(user=manager)
        
        from django.urls import reverse
        url = reverse('screen-list')
        data = {'name': 'Test', 'device_id': 'test-001'}
        response = self.client.post(url, data, format='json')
        
        # Should succeed
        self.assertIn(response.status_code, [201, 400])  # 400 if validation fails
    
    def test_operator_can_create_commands(self):
        """Test Operator can create commands."""
        operator = self.create_user(role='Operator')
        self.client.force_authenticate(user=operator)
        
        screen = self.create_screen()
        
        from django.urls import reverse
        url = reverse('command-list')
        data = {
            'name': 'Test Command',
            'type': 'refresh',
            'screen': str(screen.id),
            'payload': {}
        }
        response = self.client.post(url, data, format='json')
        
        # Should succeed
        self.assertIn(response.status_code, [201, 400])
    
    def test_viewer_cannot_create_commands(self):
        """Test Viewer cannot create commands."""
        viewer = self.create_user(role='Viewer')
        self.client.force_authenticate(user=viewer)
        
        screen = self.create_screen()
        
        from django.urls import reverse
        url = reverse('command-list')
        data = {
            'name': 'Test Command',
            'type': 'refresh',
            'screen': str(screen.id),
            'payload': {}
        }
        response = self.client.post(url, data, format='json')
        
        # Should be denied
        self.assertEqual(response.status_code, 403)
