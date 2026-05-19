"""Local (non-Stripe) trial window for new SaaS tenants."""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from accounts.models import UserSubscription

from .models import Tenant
from .pricing_models import PlatformBillingSettings


def local_trial_days() -> int:
    solo = PlatformBillingSettings.get_solo()
    return int(solo.trial_days_display or 14)


def ensure_local_trial(tenant: Tenant) -> bool:
    """
    Set trial_end from tenant.created_at + configured trial days when the tenant
    has no Stripe subscription and no trial_end yet.
    """
    if (tenant.stripe_subscription_id or '').strip():
        return False
    if tenant.trial_end:
        return False
    if tenant.subscription_status not in ('none', 'trialing', ''):
        return False

    days = local_trial_days()
    anchor = tenant.created_at or timezone.now()
    tenant.trial_end = anchor + timedelta(days=days)
    tenant.subscription_status = 'trialing'
    tenant.save(update_fields=['trial_end', 'subscription_status', 'updated_at'])
    return True


def sync_user_subscription_from_tenant(user) -> None:
    """Mirror tenant billing snapshot onto the user's UserSubscription row."""
    tenant = getattr(user, 'tenant', None)
    if not tenant:
        return
    UserSubscription.objects.update_or_create(
        user_id=user.id,
        defaults={
            'plan_key': '',
            'plan_name': tenant.plan_name or '',
            'plan_interval': tenant.plan_interval or '',
            'status': tenant.subscription_status or 'none',
            'trial_end': tenant.trial_end,
            'current_period_start': tenant.current_period_start,
            'current_period_end': tenant.current_period_end,
            'cancel_at_period_end': bool(tenant.cancel_at_period_end),
            'provider_customer_id': tenant.stripe_customer_id or '',
            'provider_subscription_id': tenant.stripe_subscription_id or '',
            'device_limit': tenant.device_limit,
            'metadata': {'source': 'tenant_sync'},
        },
    )
