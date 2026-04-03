"""Tenant API keys and outbound webhooks."""

from __future__ import annotations

import hashlib
import secrets

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TenantApiKey, TenantWebhookEndpoint


def _saas():
    return bool(getattr(settings, 'PLATFORM_SAAS_ENABLED', False))


def _tenant(user):
    return getattr(user, 'tenant', None)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tenant_api_keys(request):
    if not _saas():
        return Response({'detail': 'SaaS not enabled.'}, status=403)
    t = _tenant(request.user)
    if not t:
        return Response({'detail': 'No tenant.'}, status=400)
    if not (request.user.is_developer() or request.user.is_manager()):
        return Response({'detail': 'Forbidden.'}, status=403)

    if request.method == 'GET':
        keys = TenantApiKey.objects.filter(tenant=t, revoked_at__isnull=True).order_by('-created_at')[:50]
        return Response(
            {
                'keys': [
                    {'id': str(k.id), 'label': k.label, 'prefix': k.prefix, 'created_at': k.created_at.isoformat()}
                    for k in keys
                ]
            }
        )

    label = (request.data.get('label') or '').strip()[:128]
    raw = secrets.token_urlsafe(32)
    prefix = raw[:12]
    h = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    k = TenantApiKey.objects.create(tenant=t, label=label, prefix=prefix, key_hash=h)
    return Response(
        {
            'id': str(k.id),
            'label': k.label,
            'prefix': k.prefix,
            'secret': raw,
            'message': 'Store this secret now; it will not be shown again.',
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tenant_api_key_revoke(request, pk):
    if not _saas():
        return Response({'detail': 'SaaS not enabled.'}, status=403)
    t = _tenant(request.user)
    if not t or not (request.user.is_developer() or request.user.is_manager()):
        return Response({'detail': 'Forbidden.'}, status=403)
    from django.utils import timezone

    k = TenantApiKey.objects.filter(pk=pk, tenant=t).first()
    if not k:
        return Response({'detail': 'Not found.'}, status=404)
    k.revoked_at = timezone.now()
    k.save(update_fields=['revoked_at'])
    return Response({'status': 'ok'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tenant_webhooks(request):
    if not _saas():
        return Response({'detail': 'SaaS not enabled.'}, status=403)
    t = _tenant(request.user)
    if not t or not (request.user.is_developer() or request.user.is_manager()):
        return Response({'detail': 'Forbidden.'}, status=403)

    if request.method == 'GET':
        qs = TenantWebhookEndpoint.objects.filter(tenant=t)[:20]
        return Response(
            {
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
        )

    url = (request.data.get('url') or '').strip()
    if not url:
        return Response({'detail': 'url required'}, status=400)
    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = (parsed.hostname or '').lower()
    if hostname in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
        return Response({'detail': 'Localhost webhook URLs are not allowed.'}, status=400)
    if hostname.startswith(('10.', '192.168.', '172.16.', '172.17.', '172.18.',
                            '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
                            '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
                            '172.29.', '172.30.', '172.31.')):
        return Response({'detail': 'Private IP webhook URLs are not allowed.'}, status=400)
    secret = secrets.token_hex(32)
    w = TenantWebhookEndpoint.objects.create(
        tenant=t,
        url=url[:2048],
        signing_secret=secret,
        event_types=request.data.get('event_types') or ['*'],
    )
    return Response(
        {
            'id': str(w.id),
            'url': w.url,
            'signing_secret': secret,
            'event_types': w.event_types,
        },
        status=201,
    )
