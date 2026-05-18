"""Tenant API keys and outbound webhooks (manager / tenant-scoped user)."""

from __future__ import annotations

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .integration_helpers import (
    create_api_key,
    create_webhook,
    list_api_keys,
    list_webhooks,
    revoke_api_key,
)


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
        return Response(list_api_keys(t))

    payload = create_api_key(t, request.data.get('label'))
    return Response(payload, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tenant_api_key_revoke(request, pk):
    if not _saas():
        return Response({'detail': 'SaaS not enabled.'}, status=403)
    t = _tenant(request.user)
    if not t or not (request.user.is_developer() or request.user.is_manager()):
        return Response({'detail': 'Forbidden.'}, status=403)
    err = revoke_api_key(t, pk)
    if err:
        return err
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
        return Response(list_webhooks(t))

    payload, err = create_webhook(t, request.data.get('url') or '', request.data.get('event_types'))
    if err:
        return err
    return Response(payload, status=status.HTTP_201_CREATED)
