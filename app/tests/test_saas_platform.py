"""Tests for Platform (SaaS super-admin) API."""

import json
from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from saas_platform.models import PlatformExpense, Tenant, TenantAuditLog, TenantWebhookEndpoint


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tenant(db):
    return Tenant.objects.create(name='Acme Corp', slug='acme')


@pytest.fixture
def tenant_b(db):
    return Tenant.objects.create(name='Beta Inc', slug='beta')


@pytest.fixture
def employee_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='employee1',
        email='employee@test.com',
        password='testpass123',
        role='Employee',
        is_active=True,
    )


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


@pytest.fixture
def employee_with_tenant(db, tenant):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    u = User.objects.create_user(
        username='emp_tenant',
        email='emp_tenant@test.com',
        password='testpass123',
        role='Employee',
        is_active=True,
    )
    u.tenant = tenant
    u.save(update_fields=['tenant'])
    return u


# ---------------------------------------------------------------------------
# Existing coverage: tenant list, overview, cohorts
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenants_list_as_developer(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/tenants/')
    assert r.status_code == 200
    assert 'results' in r.data or isinstance(r.data, list)


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=False)
def test_platform_tenants_forbidden_when_disabled(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/tenants/')
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenants_denied_for_manager(manager_user):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    r = client.get('/api/platform/tenants/')
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenant_create_as_developer(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.post(
        '/api/platform/tenants/',
        {
            'name': 'Gamma Org',
            'slug': 'gamma-org',
            'subscription_status': 'trialing',
            'plan_name': 'Starter',
            'plan_interval': 'month',
            'device_limit': 25,
        },
        format='json',
    )
    assert r.status_code == 201
    assert r.data['name'] == 'Gamma Org'
    assert r.data['slug'] == 'gamma-org'
    assert Tenant.objects.filter(slug='gamma-org').exists()


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenant_update_as_developer(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.put(
        f'/api/platform/tenants/{tenant.id}/',
        {'name': 'Acme Updated', 'plan_name': 'Pro', 'subscription_status': 'active'},
        format='json',
    )
    assert r.status_code == 200
    assert r.data['name'] == 'Acme Updated'
    tenant.refresh_from_db()
    assert tenant.plan_name == 'Pro'


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenant_delete_as_developer(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.delete(f'/api/platform/tenants/{tenant.id}/')
    assert r.status_code == 200
    assert r.data['status'] == 'deleted'
    assert not Tenant.objects.filter(id=tenant.id).exists()


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenant_create_denied_for_manager(manager_user):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    r = client.post('/api/platform/tenants/', {'name': 'Nope'}, format='json')
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_tenant_access_lock_and_unlock(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    lock_r = client.post(
        f'/api/platform/tenants/{tenant.id}/access-lock/',
        {'reason': 'Security review'},
        format='json',
    )
    assert lock_r.status_code == 200
    assert lock_r.data['access_locked'] is True
    assert lock_r.data['access_lock_reason'] == 'Security review'

    unlock_r = client.post(f'/api/platform/tenants/{tenant.id}/access-unlock/')
    assert unlock_r.status_code == 200
    assert unlock_r.data['access_locked'] is False


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_user_lock_unlock_and_revoke_sessions(superadmin_user, employee_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    lock_r = client.post(
        f'/api/users/{employee_user.id}/lock/',
        {'reason': 'Policy violation'},
        format='json',
    )
    assert lock_r.status_code == 200
    employee_user.refresh_from_db()
    assert employee_user.is_admin_locked is True

    revoke_r = client.post(f'/api/users/{employee_user.id}/revoke_sessions/')
    assert revoke_r.status_code == 200
    assert 'count' in revoke_r.data

    unlock_r = client.post(f'/api/users/{employee_user.id}/unlock/')
    assert unlock_r.status_code == 200
    employee_user.refresh_from_db()
    assert employee_user.is_admin_locked is False


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_locked_user_login_blocked(superadmin_user):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    u = User.objects.create_user(
        username='locked_user',
        email='locked@example.com',
        password='StrongP@ss1234!',
        role='Employee',
    )
    client_admin = APIClient()
    client_admin.force_authenticate(user=superadmin_user)
    lock_r = client_admin.post(f'/api/users/{u.id}/lock/', {'reason': 'Incident'}, format='json')
    assert lock_r.status_code == 200

    anon = APIClient()
    login_r = anon.post(
        '/api/auth/login/',
        {'username': 'locked_user', 'password': 'StrongP@ss1234!'},
        format='json',
    )
    assert login_r.status_code == 401
    assert 'locked' in str(login_r.data.get('error', '')).lower()
    restriction = login_r.data.get('restriction')
    assert restriction is not None
    assert restriction['kind'] == 'user_admin_lock'
    assert restriction['reason'] == 'Incident'


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_tenant_locked_user_login_blocked(superadmin_user, tenant):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    u = User.objects.create_user(
        username='tenant_locked_user',
        email='tenant_locked@example.com',
        password='StrongP@ss1234!',
        role='Employee',
        tenant=tenant,
    )
    client_admin = APIClient()
    client_admin.force_authenticate(user=superadmin_user)
    lock_r = client_admin.post(
        f'/api/platform/tenants/{tenant.id}/access-lock/',
        {'reason': 'Billing hold'},
        format='json',
    )
    assert lock_r.status_code == 200

    anon = APIClient()
    login_r = anon.post(
        '/api/auth/login/',
        {'username': u.username, 'password': 'StrongP@ss1234!'},
        format='json',
    )
    assert login_r.status_code == 401
    assert 'company account' in str(login_r.data.get('error', '')).lower()
    restriction = login_r.data.get('restriction')
    assert restriction is not None
    assert restriction['kind'] == 'tenant_access_lock'
    assert restriction['reason'] == 'Billing hold'


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_user_me_exposes_lock_state(superadmin_user, employee_user):
    client_admin = APIClient()
    client_admin.force_authenticate(user=superadmin_user)
    client_admin.post(f'/api/users/{employee_user.id}/lock/', {'reason': 'Review'}, format='json')

    employee_user.refresh_from_db()
    client_emp = APIClient()
    client_emp.force_authenticate(user=employee_user)
    r = client_emp.get('/api/users/me/')
    assert r.status_code == 200
    assert r.data['is_lock_active'] is True
    assert r.data['admin_lock_reason'] == 'Review'


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_user_me_exposes_tenant_restriction(superadmin_user, tenant, employee_with_tenant):
    client_admin = APIClient()
    client_admin.force_authenticate(user=superadmin_user)
    client_admin.post(
        f'/api/platform/tenants/{tenant.id}/access-lock/',
        {'reason': 'Compliance'},
        format='json',
    )

    from django.contrib.auth import get_user_model
    User = get_user_model()
    fresh_user = User.objects.select_related('tenant').get(pk=employee_with_tenant.pk)
    client_emp = APIClient()
    client_emp.force_authenticate(user=fresh_user)
    r = client_emp.get('/api/users/me/')
    assert r.status_code == 200
    tr = r.data.get('tenant_restriction')
    assert tr is not None, f'Expected tenant_restriction in response, got keys: {list(r.data.keys())}'
    assert tr['kind'] == 'tenant_access_lock'
    assert tr['reason'] == 'Compliance'


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_overview(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/overview/')
    assert r.status_code == 200
    assert 'counts' in r.data
    assert 'health' in r.data
    assert 'revenue' in r.data
    assert 'charts' in r.data
    assert 'revenue_by_month' in r.data['charts']
    assert 'expenses_by_month' in r.data['charts']
    assert 'expense_by_category' in r.data['charts']


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_cohorts(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/cohorts/')
    assert r.status_code == 200
    assert 'cohorts' in r.data
    assert isinstance(r.data['cohorts'], list)


# ---------------------------------------------------------------------------
# Billing expenses CRUD
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_expense_create_and_list(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    create_r = client.post(
        '/api/platform/billing/expenses/',
        {
            'title': 'Cloud hosting',
            'category': 'infrastructure',
            'amount_cents': 125000,
            'spent_on': '2026-04-01',
            'tenant': str(tenant.id),
            'notes': 'Monthly infra invoice',
            'is_recurring': True,
        },
        format='json',
    )
    assert create_r.status_code == 201
    assert create_r.data['title'] == 'Cloud hosting'
    assert create_r.data['created_by'] == superadmin_user.id

    list_r = client.get('/api/platform/billing/expenses/')
    assert list_r.status_code == 200
    assert len(list_r.data['results']) >= 1


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_expense_update_and_delete(superadmin_user):
    exp = PlatformExpense.objects.create(
        title='Old cost',
        category='tools',
        amount_cents=20000,
        spent_on='2026-03-01',
    )
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    update_r = client.put(
        f'/api/platform/billing/expenses/{exp.id}/',
        {
            'title': 'Updated tooling',
            'category': 'tools',
            'amount_cents': 45000,
            'spent_on': '2026-03-01',
            'notes': 'Adjusted to annualized seat count',
            'is_recurring': False,
        },
        format='json',
    )
    assert update_r.status_code == 200
    assert update_r.data['amount_cents'] == 45000

    delete_r = client.delete(f'/api/platform/billing/expenses/{exp.id}/')
    assert delete_r.status_code == 204
    assert not PlatformExpense.objects.filter(id=exp.id).exists()


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_expense_denied_for_manager(manager_user):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    r = client.get('/api/platform/billing/expenses/')
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=False)
def test_platform_expense_saas_disabled(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/billing/expenses/')
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Impersonation (security-critical)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_impersonate_start_ok(superadmin_user, employee_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.post('/api/platform/impersonate/', {'user_id': str(employee_user.id)})
    assert r.status_code == 200
    assert 'tokens' in r.data
    assert r.data['impersonation']['active'] is True
    assert r.data['impersonation']['impersonator_id'] == str(superadmin_user.id)
    assert r.data['user']['id'] == str(employee_user.id)


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_impersonate_start_blocked_for_another_developer(superadmin_user, admin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.post('/api/platform/impersonate/', {'user_id': str(admin_user.id)})
    assert r.status_code == 403
    assert 'Developer' in r.data['detail']


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_impersonate_start_denied_for_manager(manager_user, employee_user):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    r = client.post('/api/platform/impersonate/', {'user_id': str(employee_user.id)})
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_impersonate_start_missing_user_id(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.post('/api/platform/impersonate/', {})
    assert r.status_code == 400


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=False)
def test_impersonate_start_saas_disabled(superadmin_user, employee_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.post('/api/platform/impersonate/', {'user_id': str(employee_user.id)})
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_impersonate_stop_ok(superadmin_user, employee_user):
    """Full flow: start → get admin refresh → stop with it (called as impersonated user)."""
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    start_r = client.post('/api/platform/impersonate/', {'user_id': str(employee_user.id)})
    assert start_r.status_code == 200
    admin_refresh = start_r.data['tokens']['refresh']

    from accounts.tokens import ScreenGramRefreshToken
    admin_refresh_token = ScreenGramRefreshToken.for_user(superadmin_user)

    client2 = APIClient()
    client2.force_authenticate(user=employee_user)
    stop_r = client2.post(
        '/api/platform/impersonate/stop/',
        {'admin_refresh_token': str(admin_refresh_token)},
    )
    assert stop_r.status_code == 200
    assert stop_r.data['user']['id'] == str(superadmin_user.id)
    assert stop_r.data['user']['role'] == 'Developer'


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_impersonate_stop_missing_token(employee_user):
    client = APIClient()
    client.force_authenticate(user=employee_user)
    r = client.post('/api/platform/impersonate/stop/', {})
    assert r.status_code == 400


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_impersonate_stop_invalid_token(employee_user):
    client = APIClient()
    client.force_authenticate(user=employee_user)
    r = client.post('/api/platform/impersonate/stop/', {'admin_refresh_token': 'garbage.token.value'})
    assert r.status_code == 400


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_impersonate_stop_non_developer_refresh(employee_user, manager_user):
    """Providing a refresh token for a non-Developer should be rejected."""
    from accounts.tokens import ScreenGramRefreshToken
    mgr_token = ScreenGramRefreshToken.for_user(manager_user)
    client = APIClient()
    client.force_authenticate(user=employee_user)
    r = client.post('/api/platform/impersonate/stop/', {'admin_refresh_token': str(mgr_token)})
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_impersonate_creates_audit_log(superadmin_user, employee_user, tenant):
    employee_user.tenant = tenant
    employee_user.save(update_fields=['tenant'])
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    client.post('/api/platform/impersonate/', {'user_id': str(employee_user.id)})
    log = TenantAuditLog.objects.filter(action='impersonation_start').first()
    assert log is not None
    assert log.details['target_user_id'] == str(employee_user.id)


# ---------------------------------------------------------------------------
# Feature flags (GET/PUT + validation)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_feature_flags_get(superadmin_user, tenant):
    tenant.feature_flags = {'beta_player': True}
    tenant.save(update_fields=['feature_flags'])
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get(f'/api/platform/tenants/{tenant.pk}/feature-flags/')
    assert r.status_code == 200
    assert r.data['beta_player'] is True


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_feature_flags_put_merge(superadmin_user, tenant):
    tenant.feature_flags = {'existing_flag': True}
    tenant.save(update_fields=['feature_flags'])
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.put(
        f'/api/platform/tenants/{tenant.pk}/feature-flags/',
        {'new_flag': True},
        format='json',
    )
    assert r.status_code == 200
    assert r.data['existing_flag'] is True
    assert r.data['new_flag'] is True


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_feature_flags_put_invalid_key(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.put(
        f'/api/platform/tenants/{tenant.pk}/feature-flags/',
        {'Invalid-Key!': True},
        format='json',
    )
    assert r.status_code == 400
    assert 'Invalid flag key' in r.data['detail']


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_feature_flags_put_non_object(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.put(
        f'/api/platform/tenants/{tenant.pk}/feature-flags/',
        data=json.dumps([True, False]),
        content_type='application/json',
    )
    assert r.status_code == 400


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_feature_flags_creates_audit_log(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    client.put(
        f'/api/platform/tenants/{tenant.pk}/feature-flags/',
        {'beta_widgets': True},
        format='json',
    )
    log = TenantAuditLog.objects.filter(action='feature_flags_update', tenant=tenant).first()
    assert log is not None
    assert 'beta_widgets' in log.details['keys']


# ---------------------------------------------------------------------------
# Tenant actions (manual override / sync-stripe)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_manual_override_ok(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.post(
        f'/api/platform/tenants/{tenant.pk}/manual-override/',
        {'device_limit': 50, 'notes': 'Courtesy extension'},
        format='json',
    )
    assert r.status_code == 200
    assert r.data['device_limit'] == 50
    log = TenantAuditLog.objects.filter(action='manual_override', tenant=tenant).first()
    assert log is not None


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_sync_stripe_no_subscription(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.post(f'/api/platform/tenants/{tenant.pk}/sync-stripe/')
    assert r.status_code == 400
    assert 'stripe_subscription_id' in r.data['detail']


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True, STRIPE_SECRET_KEY='sk_test_x')
def test_sync_stripe_fetch_fails(superadmin_user, tenant):
    tenant.stripe_subscription_id = 'sub_test123'
    tenant.save(update_fields=['stripe_subscription_id'])
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    with patch('saas_platform.services.fetch_stripe_subscription', return_value=None):
        r = client.post(f'/api/platform/tenants/{tenant.pk}/sync-stripe/')
    assert r.status_code == 502


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_tenant_audit_log_endpoint(superadmin_user, tenant):
    TenantAuditLog.objects.create(tenant=tenant, action='test_action', details={'key': 'val'})
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get(f'/api/platform/tenants/{tenant.pk}/audit-log/')
    assert r.status_code == 200
    assert isinstance(r.data, list)
    assert r.data[0]['action'] == 'test_action'


# ---------------------------------------------------------------------------
# Export users.xlsx
# ---------------------------------------------------------------------------

_has_openpyxl = False
try:
    import openpyxl  # noqa: F401
    _has_openpyxl = True
except ImportError:
    pass


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_export_users_all(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/exports/users.xlsx?scope=all')
    if _has_openpyxl:
        assert r.status_code == 200
        assert 'spreadsheetml' in r['Content-Type']
        assert 'users_all.xlsx' in r.get('Content-Disposition', '')
    else:
        assert r.status_code == 503


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_export_users_tenant_admins(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/exports/users.xlsx?scope=tenant_admins')
    if _has_openpyxl:
        assert r.status_code == 200
        assert 'users_tenant_admins.xlsx' in r.get('Content-Disposition', '')
    else:
        assert r.status_code == 503


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_export_users_invalid_scope(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/exports/users.xlsx?scope=bogus')
    if _has_openpyxl:
        assert r.status_code == 400
    else:
        assert r.status_code == 503


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_export_denied_for_manager(manager_user):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    r = client.get('/api/platform/exports/users.xlsx?scope=all')
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=False)
def test_export_saas_disabled(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/exports/users.xlsx?scope=all')
    assert r.status_code in (403, 503)


# ---------------------------------------------------------------------------
# Capacity / Communications / System Health endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_capacity(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/capacity/')
    assert r.status_code == 200
    assert 'tenants' in r.data


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_communications(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/communications/')
    assert r.status_code == 200
    assert 'results' in r.data


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_system_health(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/system-health/')
    assert r.status_code == 200
    assert 'checks' in r.data
    assert r.data['checks']['database']['ok'] is True


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=False)
def test_platform_system_health_saas_off(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/system-health/')
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Webhook URL validation (integration_views)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_webhook_create_valid(manager_with_tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    r = client.post(
        '/api/platform/integrations/webhooks/',
        {'url': 'https://hooks.example.com/receive'},
        format='json',
    )
    assert r.status_code == 201
    assert r.data['url'] == 'https://hooks.example.com/receive'
    assert r.data['signing_secret']


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_webhook_create_localhost_blocked(manager_with_tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    r = client.post(
        '/api/platform/integrations/webhooks/',
        {'url': 'http://localhost:8000/hook'},
        format='json',
    )
    assert r.status_code == 400
    assert 'Localhost' in r.data['detail']


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_webhook_create_private_ip_blocked(manager_with_tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    r = client.post(
        '/api/platform/integrations/webhooks/',
        {'url': 'http://10.0.0.1/hook'},
        format='json',
    )
    assert r.status_code == 400
    assert 'Private' in r.data['detail']


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_webhook_create_no_url(manager_with_tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    r = client.post(
        '/api/platform/integrations/webhooks/',
        {},
        format='json',
    )
    assert r.status_code == 400


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_webhook_denied_for_employee(employee_with_tenant):
    client = APIClient()
    client.force_authenticate(user=employee_with_tenant)
    r = client.post(
        '/api/platform/integrations/webhooks/',
        {'url': 'https://example.com/hook'},
        format='json',
    )
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Billing checkout/portal (permission matrix)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True, STRIPE_PRICE_ID='', STRIPE_SECRET_KEY='')
def test_billing_checkout_no_stripe_config(manager_with_tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    r = client.post('/api/platform/billing/checkout-session/')
    assert r.status_code == 503


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_billing_checkout_denied_employee(employee_with_tenant):
    client = APIClient()
    client.force_authenticate(user=employee_with_tenant)
    r = client.post('/api/platform/billing/checkout-session/')
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=False)
def test_billing_checkout_saas_off(manager_with_tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    r = client.post('/api/platform/billing/checkout-session/')
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_billing_portal_no_customer(manager_with_tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    r = client.post('/api/platform/billing/portal-session/')
    assert r.status_code == 400
    assert 'Stripe customer' in r.data['detail']


# ---------------------------------------------------------------------------
# Stripe webhook (signature, idempotency)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=False)
def test_stripe_webhook_saas_off():
    client = APIClient()
    r = client.post('/api/platform/stripe/webhook/', data=b'{}', content_type='application/json')
    assert r.status_code == 404


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True, STRIPE_WEBHOOK_SECRET='')
def test_stripe_webhook_no_secret():
    client = APIClient()
    r = client.post(
        '/api/platform/stripe/webhook/',
        data=b'{}',
        content_type='application/json',
        HTTP_STRIPE_SIGNATURE='v1=abc',
    )
    # 400 when stripe is installed (secret not configured), 500 when stripe pkg absent
    assert r.status_code in (400, 500)


# ---------------------------------------------------------------------------
# API key endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_api_key_create_and_list(manager_with_tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    r = client.post('/api/platform/integrations/api-keys/', {'label': 'My key'}, format='json')
    assert r.status_code == 201
    assert 'secret' in r.data

    r2 = client.get('/api/platform/integrations/api-keys/')
    assert r2.status_code == 200
    assert len(r2.data['keys']) == 1
    assert r2.data['keys'][0]['label'] == 'My key'


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_api_key_revoke(manager_with_tenant):
    client = APIClient()
    client.force_authenticate(user=manager_with_tenant)
    create_r = client.post('/api/platform/integrations/api-keys/', {'label': 'Temp'}, format='json')
    key_id = create_r.data['id']
    r = client.post(f'/api/platform/integrations/api-keys/{key_id}/revoke/')
    assert r.status_code == 200

    r2 = client.get('/api/platform/integrations/api-keys/')
    assert len(r2.data['keys']) == 0


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_api_key_denied_for_employee(employee_with_tenant):
    client = APIClient()
    client.force_authenticate(user=employee_with_tenant)
    r = client.get('/api/platform/integrations/api-keys/')
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Unauthenticated access (all platform endpoints)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_platform_unauthenticated():
    client = APIClient()
    endpoints = [
        '/api/platform/tenants/',
        '/api/platform/overview/',
        '/api/platform/cohorts/',
        '/api/platform/capacity/',
        '/api/platform/communications/',
        '/api/platform/system-health/',
        '/api/platform/exports/users.xlsx',
        '/api/platform/billing/expenses/',
    ]
    for url in endpoints:
        r = client.get(url)
        assert r.status_code in (401, 403), f'{url} returned {r.status_code}'


# ---------------------------------------------------------------------------
# Tenant license management (Phase 5 parity)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_tenant_license_get_creates_default(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get(f'/api/platform/tenants/{tenant.id}/license/')
    assert r.status_code == 200
    assert r.data['license_status'] == 'inactive'
    assert r.data['is_entitled'] is False


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_tenant_license_update(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.put(
        f'/api/platform/tenants/{tenant.id}/license/',
        {'license_status': 'active', 'license_key': 'abc-123', 'offline_grace_hours': 48},
        format='json',
    )
    assert r.status_code == 200
    assert r.data['license_status'] == 'active'
    assert r.data['is_entitled'] is True
    assert r.data['offline_grace_hours'] == 48


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_tenant_license_denied_for_manager(manager_user, tenant):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    r = client.get(f'/api/platform/tenants/{tenant.id}/license/')
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_tenant_license_enforcement_logs(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    client.put(
        f'/api/platform/tenants/{tenant.id}/license/',
        {'license_status': 'active'},
        format='json',
    )
    r = client.get(f'/api/platform/tenants/{tenant.id}/license/enforcement-logs/')
    assert r.status_code == 200
    assert len(r.data['results']) >= 1
    assert r.data['results'][0]['action'] == 'license_updated'


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=False)
def test_tenant_license_saas_disabled(superadmin_user, tenant):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get(f'/api/platform/tenants/{tenant.id}/license/')
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Audit log immutability and export
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_audit_log_export_csv(superadmin_user):
    from core.models import AuditLog
    AuditLog.objects.create(
        username='testuser', action_type='login',
        description='Test login', severity='low',
    )
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/core/audit-logs/export/')
    assert r.status_code == 200
    assert 'text/csv' in r['Content-Type']
    assert 'testuser' in r.content.decode()


@pytest.mark.django_db
def test_audit_log_export_denied_for_manager(manager_user):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    r = client.get('/api/core/audit-logs/export/')
    assert r.status_code == 403


@pytest.mark.django_db
def test_audit_log_archived_hidden_by_default(superadmin_user):
    from core.models import AuditLog
    visible = AuditLog.objects.create(
        username='visible', action_type='login', severity='low',
    )
    archived = AuditLog.objects.create(
        username='archived', action_type='login', severity='low', is_archived=True,
    )
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/core/audit-logs/')
    usernames = [log['username'] for log in (r.data.get('results') or r.data)]
    assert 'visible' in usernames
    assert 'archived' not in usernames

    r2 = client.get('/api/core/audit-logs/?include_archived=true')
    usernames2 = [log['username'] for log in (r2.data.get('results') or r2.data)]
    assert 'archived' in usernames2


# ---------------------------------------------------------------------------
# SaaS gating on new endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=False)
def test_expense_saas_gating(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/billing/expenses/')
    assert r.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_SAAS_ENABLED=True)
def test_tenant_crud_full_lifecycle(superadmin_user):
    """Full tenant lifecycle: create, update, lock, unlock, feature-flags, delete."""
    client = APIClient()
    client.force_authenticate(user=superadmin_user)

    r = client.post('/api/platform/tenants/', {'name': 'Lifecycle Test'}, format='json')
    assert r.status_code == 201
    tid = r.data['id']

    r = client.put(f'/api/platform/tenants/{tid}/', {'name': 'Updated Name', 'plan_name': 'Pro'}, format='json')
    assert r.status_code == 200
    assert r.data['name'] == 'Updated Name'

    r = client.post(f'/api/platform/tenants/{tid}/access-lock/', {'reason': 'Test'}, format='json')
    assert r.status_code == 200
    assert r.data['access_locked'] is True

    r = client.post(f'/api/platform/tenants/{tid}/access-unlock/')
    assert r.status_code == 200
    assert r.data['access_locked'] is False

    r = client.put(f'/api/platform/tenants/{tid}/feature-flags/', {'beta_v2': True}, format='json')
    assert r.status_code == 200
    assert r.data['beta_v2'] is True

    r = client.delete(f'/api/platform/tenants/{tid}/')
    assert r.status_code == 200
    assert r.data['status'] == 'deleted'
