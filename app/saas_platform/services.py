"""Stripe subscription sync and tenant billing helpers."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from accounts.models import UserSubscription
from .models import Tenant, TenantInvoice
from .stripe_config import get_stripe_secret_key

logger = logging.getLogger(__name__)


def _ts_to_aware_dt(ts: Any) -> Optional[datetime]:
    if ts is None:
        return None
    try:
        if hasattr(ts, 'isoformat'):
            return timezone.make_aware(ts, timezone=dt_timezone.utc) if timezone.is_naive(ts) else ts
        n = int(ts)
        return datetime.fromtimestamp(n, tz=dt_timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def _device_limit_from_stripe_subscription(sub: dict[str, Any], line_items: list | None) -> Any:
    """
    Return None to leave tenant.device_limit unchanged, 'unlimited', or a positive int.
    Prefer subscription metadata from Checkout; fall back to per-screen quantity.
    """
    meta = sub.get('metadata') or {}
    raw = meta.get('device_limit')
    if raw is not None and str(raw).strip() != '':
        s = str(raw).strip().lower()
        if s == 'unlimited':
            return 'unlimited'
        if s.isdigit():
            return int(s)

    plan_key = (meta.get('plan_key') or '').strip()
    if plan_key == 'per_screen' and line_items:
        row0 = line_items[0]
        q = row0.get('quantity') if isinstance(row0, dict) else getattr(row0, 'quantity', None)
        if q is not None:
            try:
                return max(1, int(q))
            except (TypeError, ValueError):
                pass
    return None


def sync_tenant_from_stripe_subscription(tenant: Tenant, sub: dict[str, Any]) -> None:
    """Update tenant fields from a Stripe Subscription object (dict or StripeObject)."""
    status = sub.get('status') or 'none'
    tenant.stripe_subscription_id = sub.get('id') or tenant.stripe_subscription_id
    valid_statuses = {c[0] for c in Tenant.SUBSCRIPTION_STATUS_CHOICES}
    tenant.subscription_status = status if status in valid_statuses else 'none'

    items = sub.get('items', {})
    data = items.get('data') if isinstance(items, dict) else getattr(items, 'data', None)
    if data and len(data) > 0:
        price = data[0].get('price') if isinstance(data[0], dict) else getattr(data[0], 'price', None)
        if isinstance(price, dict):
            tenant.plan_interval = (price.get('recurring') or {}).get('interval', '') or ''
            nickname = price.get('nickname') or ''
            pid = price.get('id', '')
            tenant.plan_name = nickname or pid or tenant.plan_name
        elif price is not None:
            rec = getattr(price, 'recurring', None)
            tenant.plan_interval = getattr(rec, 'interval', '') if rec else ''
            tenant.plan_name = getattr(price, 'nickname', None) or getattr(price, 'id', '') or tenant.plan_name

    dl = _device_limit_from_stripe_subscription(sub, list(data) if data else None)
    if dl == 'unlimited':
        tenant.device_limit = None
    elif isinstance(dl, int):
        tenant.device_limit = dl

    tenant.current_period_start = _ts_to_aware_dt(sub.get('current_period_start'))
    tenant.current_period_end = _ts_to_aware_dt(sub.get('current_period_end'))
    tenant.trial_end = _ts_to_aware_dt(sub.get('trial_end'))
    tenant.cancel_at_period_end = bool(sub.get('cancel_at_period_end'))

    update_fields = [
        'stripe_subscription_id',
        'subscription_status',
        'plan_name',
        'plan_interval',
        'current_period_start',
        'current_period_end',
        'trial_end',
        'cancel_at_period_end',
        'updated_at',
    ]
    if dl is not None:
        update_fields.append('device_limit')

    tenant.save(update_fields=update_fields)
    _sync_user_subscriptions_from_tenant(tenant, sub)


def _extract_plan_key(sub: dict[str, Any]) -> str:
    meta = sub.get('metadata') or {}
    return (meta.get('plan_key') or '').strip()


def _sync_user_subscriptions_from_tenant(tenant: Tenant, sub: dict[str, Any]) -> None:
    """Propagate the Stripe-derived tenant snapshot to all users in that tenant."""
    users_qs = tenant.users.all().only('id')
    if not users_qs.exists():
        return

    status = sub.get('status') or tenant.subscription_status or 'none'
    plan_key = _extract_plan_key(sub)
    plan_name = tenant.plan_name or ''
    plan_interval = tenant.plan_interval or ''
    trial_end = tenant.trial_end
    current_period_start = tenant.current_period_start
    current_period_end = tenant.current_period_end
    cancel_at_period_end = bool(tenant.cancel_at_period_end)
    provider_customer_id = tenant.stripe_customer_id or ''
    provider_subscription_id = tenant.stripe_subscription_id or ''
    device_limit = tenant.device_limit
    metadata = sub.get('metadata') or {}

    for user in users_qs:
        UserSubscription.objects.update_or_create(
            user_id=user.id,
            defaults={
                'plan_key': plan_key,
                'plan_name': plan_name,
                'plan_interval': plan_interval,
                'status': status,
                'trial_end': trial_end,
                'current_period_start': current_period_start,
                'current_period_end': current_period_end,
                'cancel_at_period_end': cancel_at_period_end,
                'provider_customer_id': provider_customer_id,
                'provider_subscription_id': provider_subscription_id,
                'device_limit': device_limit,
                'metadata': metadata,
            },
        )


def upsert_invoice_from_stripe(tenant: Tenant, inv: dict[str, Any]) -> TenantInvoice:
    stripe_id = inv.get('id')
    defaults = {
        'tenant': tenant,
        'number': inv.get('number') or '',
        'amount_due': int(inv.get('amount_due') or 0),
        'amount_paid': int(inv.get('amount_paid') or 0),
        'currency': (inv.get('currency') or 'usd'),
        'status': inv.get('status') or 'open',
        'hosted_invoice_url': inv.get('hosted_invoice_url') or '',
        'invoice_pdf': inv.get('invoice_pdf') or '',
        'period_start': _ts_to_aware_dt(inv.get('period_start')),
        'period_end': _ts_to_aware_dt(inv.get('period_end')),
    }
    obj, _ = TenantInvoice.objects.update_or_create(
        stripe_invoice_id=stripe_id,
        defaults=defaults,
    )
    return obj


def find_tenant_by_stripe_customer(customer_id: str) -> Optional[Tenant]:
    if not customer_id:
        return None
    return Tenant.objects.filter(stripe_customer_id=customer_id).first()


@transaction.atomic
def apply_payment_failed(tenant: Tenant, at: Optional[datetime] = None) -> None:
    when = at or timezone.now()
    tenant.last_payment_failed_at = when
    tenant.payment_failed_count = (tenant.payment_failed_count or 0) + 1
    grace_days = int(getattr(settings, 'STRIPE_INTERNAL_GRACE_DAYS', 3) or 3)
    tenant.billing_grace_until = when + timedelta(days=grace_days)
    tenant.save(
        update_fields=[
            'last_payment_failed_at',
            'payment_failed_count',
            'billing_grace_until',
            'updated_at',
        ]
    )


def fetch_stripe_subscription(subscription_id: str) -> Optional[dict[str, Any]]:
    secret = get_stripe_secret_key()
    if not subscription_id or not secret:
        return None
    try:
        import stripe

        stripe.api_key = secret
        sub = stripe.Subscription.retrieve(subscription_id)
        return sub.to_dict() if hasattr(sub, 'to_dict') else dict(sub)
    except Exception as e:
        logger.warning('Stripe retrieve subscription failed: %s', e)
        return None
