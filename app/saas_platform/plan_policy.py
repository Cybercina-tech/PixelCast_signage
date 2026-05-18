"""
Tenant plan limits — enforce quotas when PLATFORM_SAAS_ENABLED.
"""

from __future__ import annotations

from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError


def tenant_for_user(user):
    tid = getattr(user, 'tenant_id', None)
    if not tid:
        return None
    from .models import Tenant

    return Tenant.objects.filter(pk=tid).first()


def count_screens_for_tenant(tenant_id) -> int:
    from signage.models import Screen

    return Screen.objects.filter(owner__tenant_id=tenant_id).count()


def tenant_has_manual_access(tenant) -> bool:
    until = getattr(tenant, 'manual_access_until', None)
    return bool(until and until > timezone.now())


def assert_can_create_screen(user) -> None:
    """Raise ValidationError if tenant is at device_limit."""
    if not getattr(settings, 'PLATFORM_SAAS_ENABLED', False):
        return
    tenant = tenant_for_user(user)
    if not tenant:
        return
    if tenant_has_manual_access(tenant):
        return
    limit = tenant.device_limit
    if limit is None:
        return
    n = count_screens_for_tenant(tenant.id)
    if n >= limit:
        raise ValidationError(
            {
                'detail': f'Screen limit reached for your plan ({limit}). Upgrade or remove a screen.',
                'code': 'device_limit_exceeded',
            }
        )
