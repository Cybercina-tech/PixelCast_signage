"""
Tests for permission and authorization logic.
"""
from django.test import TestCase
from tests.base import BaseAPITestCase
from accounts.permissions import RolePermissions


class PermissionTests(BaseAPITestCase):
    """Tests for permission checking."""

    def test_developer_permissions(self):
        dev = self.create_user(role='Developer', is_superuser=True, is_staff=True)
        screen = self.create_screen()
        template = self.create_template()
        self.assertTrue(RolePermissions.can_edit_resource(dev, screen))
        self.assertTrue(RolePermissions.can_edit_resource(dev, template))
        self.assertTrue(RolePermissions.can_view_resource(dev, screen))

    def test_manager_permissions(self):
        manager = self.create_user(role='Manager', organization_name='Org1')
        other_manager = self.create_user(role='Manager', organization_name='Org2')
        own_screen = self.create_screen(owner=manager)
        self.assertTrue(RolePermissions.can_edit_resource(manager, own_screen))
        other_screen = self.create_screen(owner=other_manager)
        self.assertFalse(RolePermissions.can_edit_resource(manager, other_screen))

    def test_employee_permissions(self):
        employee = self.create_user(role='Employee')
        own_screen = self.create_screen(owner=employee)
        self.assertTrue(RolePermissions.can_view_resource(employee, own_screen))

    def test_command_execution_roles(self):
        manager = self.create_user(role='Manager')
        employee = self.create_user(role='Employee')
        self.assertTrue(manager.can_execute_commands())
        self.assertFalse(employee.can_execute_commands())


class APIPermissionTests(BaseAPITestCase):
    """Tests for API endpoint permissions."""

    def test_unauthorized_access_denied(self):
        self.client.force_authenticate(user=None)
        from django.urls import reverse
        url = reverse('screen-list')
        response = self.client.get(url)
        self.assertUnauthorized(response)

    def test_employee_can_create_screens(self):
        employee = self.create_user(role='Employee')
        self.client.force_authenticate(user=employee)
        from django.urls import reverse
        url = reverse('screen-list')
        data = {'name': 'Test', 'device_id': 'test-001'}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_manager_can_create_screens(self):
        manager = self.create_user(role='Manager')
        self.client.force_authenticate(user=manager)
        from django.urls import reverse
        url = reverse('screen-list')
        data = {'name': 'Test', 'device_id': 'test-001'}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_manager_can_create_commands(self):
        manager = self.create_user(role='Manager')
        self.client.force_authenticate(user=manager)
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
        self.assertIn(response.status_code, [201, 400])

    def test_employee_cannot_create_commands(self):
        employee = self.create_user(role='Employee')
        self.client.force_authenticate(user=employee)
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
        self.assertEqual(response.status_code, 403)
