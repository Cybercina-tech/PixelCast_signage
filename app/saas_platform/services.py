"""Stripe subscription sync and tenant billing helpers."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Tenant, TenantInvoice

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

    tenant.current_period_start = _ts_to_aware_dt(sub.get('current_period_start'))
    tenant.current_period_end = _ts_to_aware_dt(sub.get('current_period_end'))
    tenant.trial_end = _ts_to_aware_dt(sub.get('trial_end'))
    tenant.cancel_at_period_end = bool(sub.get('cancel_at_period_end'))

    tenant.save(
        update_fields=[
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
    grace_days = int(getattr(settings, 'STRIPE_GRACE_PERIOD_DAYS', 7) or 7)
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
    if not subscription_id or not getattr(settings, 'STRIPE_SECRET_KEY', ''):
        return None
    try:
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        sub = stripe.Subscription.retrieve(subscription_id)
        return sub.to_dict() if hasattr(sub, 'to_dict') else dict(sub)
    except Exception as e:
        logger.warning('Stripe retrieve subscription failed: %s', e)
        return None
