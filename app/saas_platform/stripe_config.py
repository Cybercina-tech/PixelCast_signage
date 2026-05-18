"""Stripe runtime configuration helpers (DB-first, env fallback)."""

from __future__ import annotations

from django.conf import settings

from .pricing_models import StripeBillingConfig


def get_stripe_billing_config() -> StripeBillingConfig:
    return StripeBillingConfig.get_solo()


def get_stripe_secret_key() -> str:
    cfg = get_stripe_billing_config()
    db_value = cfg.get_secret_key().strip()
    if db_value:
        return db_value
    return (getattr(settings, 'STRIPE_SECRET_KEY', '') or '').strip()


def get_stripe_webhook_secret() -> str:
    cfg = get_stripe_billing_config()
    db_value = cfg.get_webhook_secret().strip()
    if db_value:
        return db_value
    return (getattr(settings, 'STRIPE_WEBHOOK_SECRET', '') or '').strip()


def get_stripe_publishable_key() -> str:
    cfg = get_stripe_billing_config()
    db_value = (cfg.publishable_key or '').strip()
    if db_value:
        return db_value
    return (getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '') or '').strip()
