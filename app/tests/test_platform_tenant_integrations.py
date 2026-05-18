"""Platform-admin tenant integration endpoints (Developer, per-tenant)."""

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from saas_platform.models import Tenant, TenantApiKey, TenantWebhookEndpoint


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(name='Acme Corp', slug='acme')


@pytest.fixture
def manager_with_tenant(db, tenant):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    u = User.objects.create_user(
        username='mgr_tenant',
        email='mgr_tenant@test.com',
        password='testpass123',
        role='Manager',
        is_active=True,
    )
    u.tenant = tenant
    u.save(update_fields=['tenant'])
    return u


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenant_api_keys(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    base = f'/api/platform/tenants/{tenant.id}/integrations/api-keys/'

    r = client.post(base, {'label': 'Ops'}, format='json')
    assert r.status_code == 201
    assert 'secret' in r.data

    r2 = client.get(base)
    assert r2.status_code == 200
    assert len(r2.data['keys']) == 1

    key_id = r2.data['keys'][0]['id']
    r3 = client.post(f'{base}{key_id}/revoke/')
    assert r3.status_code == 200
    assert TenantApiKey.objects.filter(tenant=tenant, revoked_at__isnull=True).count() == 0


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenant_webhooks(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    base = f'/api/platform/tenants/{tenant.id}/integrations/webhooks/'

    r = client.post(base, {'url': 'https://hooks.example.com/pixelcast'}, format='json')
    assert r.status_code == 201
    assert 'signing_secret' in r.data
    wh_id = r.data['id']

    r2 = client.get(base)
    assert r2.status_code == 200
    assert len(r2.data['webhooks']) == 1

    r3 = client.patch(f'{base}{wh_id}/', {'is_active': False}, format='json')
    assert r3.status_code == 200
    assert r3.data['is_active'] is False

    r4 = client.delete(f'{base}{wh_id}/')
    assert r4.status_code == 204
    assert TenantWebhookEndpoint.objects.filter(tenant=tenant).count() == 0


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenant_integrations_denied_for_manager(manager_with_tenant, tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    r = client.get(f'/api/platform/tenants/{tenant.id}/integrations/api-keys/')
    assert r.status_code == 403
