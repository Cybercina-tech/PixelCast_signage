"""Shared tenant API key / webhook logic for manager and platform-admin APIs."""

from __future__ import annotations

import hashlib
import secrets
from typing import Any
from urllib.parse import urlparse

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from .models import Tenant, TenantApiKey, TenantWebhookEndpoint


def validate_webhook_url(url: str) -> str | None:
    """Return error message if URL is invalid; None if OK."""
    url = (url or '').strip()
    if not url:
        return 'url required'
    parsed = urlparse(url)
    hostname = (parsed.hostname or '').lower()
    if hostname in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
        return 'Localhost webhook URLs are not allowed.'
    private_prefixes = (
        '10.', '192.168.',
        '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.',
        '172.22.', '172.23.', '172.24.', '172.25.', '172.26.', '172.27.',
        '172.28.', '172.29.', '172.30.', '172.31.',
    )
    if hostname.startswith(private_prefixes):
        return 'Private IP webhook URLs are not allowed.'
    return None


def list_api_keys(tenant: Tenant) -> dict[str, Any]:
    keys = TenantApiKey.objects.filter(tenant=tenant, revoked_at__isnull=True).order_by('-created_at')[:50]
    return {
        'keys': [
            {
                'id': str(k.id),
                'label': k.label,
                'prefix': k.prefix,
                'created_at': k.created_at.isoformat(),
            }
            for k in keys
        ]
    }


def create_api_key(tenant: Tenant, label: str) -> dict[str, Any]:
    label = (label or '').strip()[:128]
    raw = secrets.token_urlsafe(32)
    prefix = raw[:12]
    h = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    k = TenantApiKey.objects.create(tenant=tenant, label=label, prefix=prefix, key_hash=h)
    return {
        'id': str(k.id),
        'label': k.label,
        'prefix': k.prefix,
        'secret': raw,
        'message': 'Store this secret now; it will not be shown again.',
    }


def revoke_api_key(tenant: Tenant, pk) -> Response | None:
    k = TenantApiKey.objects.filter(pk=pk, tenant=tenant).first()
    if not k:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    k.revoked_at = timezone.now()
    k.save(update_fields=['revoked_at'])
    return None


def list_webhooks(tenant: Tenant) -> dict[str, Any]:
    qs = TenantWebhookEndpoint.objects.filter(tenant=tenant).order_by('-created_at')[:20]
    return {
        'webhooks': [
            {
                'id': str(w.id),
                'url': w.url,
                'event_types': w.event_types,
                'is_active': w.is_active,
                'created_at': w.created_at.isoformat(),
            }
            for w in qs
        ]
    }


def create_webhook(tenant: Tenant, url: str, event_types=None) -> tuple[dict[str, Any] | None, Response | None]:
    err = validate_webhook_url(url)
    if err:
        return None, Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)
    secret = secrets.token_hex(32)
    w = TenantWebhookEndpoint.objects.create(
        tenant=tenant,
        url=url.strip()[:2048],
        signing_secret=secret,
        event_types=event_types or ['*'],
    )
    return {
        'id': str(w.id),
        'url': w.url,
        'signing_secret': secret,
        'event_types': w.event_types,
    }, None


def patch_webhook(tenant: Tenant, pk, data: dict) -> tuple[dict[str, Any] | None, Response | None]:
    w = TenantWebhookEndpoint.objects.filter(pk=pk, tenant=tenant).first()
    if not w:
        return None, Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    if 'url' in data:
        err = validate_webhook_url(data['url'])
        if err:
            return None, Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)
        w.url = str(data['url']).strip()[:2048]
    if 'is_active' in data:
        w.is_active = bool(data['is_active'])
    if 'event_types' in data:
        w.event_types = data['event_types'] or ['*']
    w.save()
    return {
        'id': str(w.id),
        'url': w.url,
        'event_types': w.event_types,
        'is_active': w.is_active,
        'created_at': w.created_at.isoformat(),
    }, None


def delete_webhook(tenant: Tenant, pk) -> Response | None:
    w = TenantWebhookEndpoint.objects.filter(pk=pk, tenant=tenant).first()
    if not w:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    w.delete()
    return None
