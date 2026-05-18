"""Platform-admin (Developer) tenant integrations — scoped by tenant_id."""

from __future__ import annotations

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .integration_helpers import (
    create_api_key,
    create_webhook,
    delete_webhook,
    list_api_keys,
    list_webhooks,
    patch_webhook,
    revoke_api_key,
)
from .models import Tenant, TenantAuditLog
from .permissions import IsDeveloper


def _saas():
    return bool(getattr(settings, 'PLATFORM_SAAS_ENABLED', False))


def _audit(tenant: Tenant, actor, action: str, details: dict):
    TenantAuditLog.objects.create(tenant=tenant, actor=actor, action=action, details=details)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_tenant_api_keys(request, tenant_id):
    if not _saas():
        return Response({'detail': 'SaaS not enabled.'}, status=403)
    tenant = get_object_or_404(Tenant, pk=tenant_id)
    if request.method == 'GET':
        return Response(list_api_keys(tenant))
    payload = create_api_key(tenant, request.data.get('label'))
    _audit(tenant, request.user, 'integration_api_key_created', {'key_id': payload['id']})
    return Response(payload, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_tenant_api_key_revoke(request, tenant_id, pk):
    if not _saas():
        return Response({'detail': 'SaaS not enabled.'}, status=403)
    tenant = get_object_or_404(Tenant, pk=tenant_id)
    err = revoke_api_key(tenant, pk)
    if err:
        return err
    _audit(tenant, request.user, 'integration_api_key_revoked', {'key_id': str(pk)})
    return Response({'status': 'ok'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_tenant_webhooks(request, tenant_id):
    if not _saas():
        return Response({'detail': 'SaaS not enabled.'}, status=403)
    tenant = get_object_or_404(Tenant, pk=tenant_id)
    if request.method == 'GET':
        return Response(list_webhooks(tenant))
    payload, err = create_webhook(
        tenant,
        request.data.get('url') or '',
        request.data.get('event_types'),
    )
    if err:
        return err
    _audit(tenant, request.user, 'integration_webhook_created', {'webhook_id': payload['id']})
    return Response(payload, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_tenant_webhook_detail(request, tenant_id, pk):
    if not _saas():
        return Response({'detail': 'SaaS not enabled.'}, status=403)
    tenant = get_object_or_404(Tenant, pk=tenant_id)
    if request.method == 'DELETE':
        err = delete_webhook(tenant, pk)
        if err:
            return err
        _audit(tenant, request.user, 'integration_webhook_deleted', {'webhook_id': str(pk)})
        return Response(status=status.HTTP_204_NO_CONTENT)
    payload, err = patch_webhook(tenant, pk, request.data)
    if err:
        return err
    _audit(tenant, request.user, 'integration_webhook_updated', {'webhook_id': str(pk)})
    return Response(payload)
