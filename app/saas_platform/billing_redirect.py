"""Validate Stripe Checkout / Portal redirect URLs (same-origin policy)."""

from __future__ import annotations

from urllib.parse import urlparse

from django.conf import settings


def billing_redirect_base() -> str:
    return (getattr(settings, 'PUBLIC_WEB_APP_URL', '') or 'http://localhost:5173').rstrip('/')


def validate_billing_redirect_url(url: str, *, field_name: str = 'url') -> str:
    """
    Allow only absolute http(s) URLs on the configured PUBLIC_WEB_APP_URL origin.
    Rejects open redirects and javascript/data schemes.
    """
    raw = (url or '').strip()
    if not raw:
        raise ValueError(f'{field_name} is required')
    parsed = urlparse(raw)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f'{field_name} must use http or https')
    if not parsed.netloc:
        raise ValueError(f'{field_name} must be absolute')
    base = urlparse(billing_redirect_base())
    if parsed.scheme != base.scheme or parsed.netloc != base.netloc:
        raise ValueError(f'{field_name} must stay on {base.scheme}://{base.netloc}')
    return raw
