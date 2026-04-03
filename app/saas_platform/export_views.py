"""Platform user export (XLSX) for super-admin."""

from __future__ import annotations

import logging

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsDeveloper

logger = logging.getLogger(__name__)

try:
    import openpyxl  # noqa: F401
    _HAS_OPENPYXL = True
except ImportError:
    _HAS_OPENPYXL = False


def _saas_enabled():
    return bool(getattr(settings, 'PLATFORM_SAAS_ENABLED', False))


VALID_SCOPES = ('all', 'tenant_admins')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeveloper])
def export_users_xlsx(request):
    if not _saas_enabled():
        return Response(
            {'detail': 'Platform SaaS features are disabled.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    if not _HAS_OPENPYXL:
        return Response(
            {'detail': 'openpyxl is not installed on this server.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    scope = request.query_params.get('scope', 'all')
    if scope not in VALID_SCOPES:
        return Response(
            {'detail': f'Invalid scope. Choose from: {", ".join(VALID_SCOPES)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from accounts.models import User

    if scope == 'tenant_admins':
        qs = User.objects.filter(
            role__in=['Developer', 'Manager'],
            tenant__isnull=False,
        ).select_related('tenant').order_by('tenant__name', 'email')
        filename = 'users_tenant_admins.xlsx'
    else:
        qs = User.objects.all().select_related('tenant').order_by('email')
        filename = 'users_all.xlsx'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Users'
    headers = ['Email', 'Username', 'Role', 'Tenant', 'Active', 'Date Joined']
    ws.append(headers)
    for u in qs.iterator():
        ws.append([
            u.email,
            u.username,
            u.role,
            u.tenant.name if u.tenant else '',
            u.is_active,
            u.date_joined.isoformat() if u.date_joined else '',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response
