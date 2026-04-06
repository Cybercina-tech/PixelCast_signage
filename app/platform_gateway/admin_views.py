"""Super-admin (Developer) API for CodeCanyon gateway instances."""

from __future__ import annotations

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from saas_platform.permissions import IsDeveloper

from .models import InstanceRegistry, InstanceUsageLog


def _saas_and_gateway():
    if not getattr(settings, "PLATFORM_SAAS_ENABLED", False):
        return False
    if not getattr(settings, "PLATFORM_GATEWAY_ENABLED", False):
        return False
    return True


def _serialize_row(inst: InstanceRegistry, last_usage: InstanceUsageLog | None) -> dict:
    return {
        "id": str(inst.id),
        "domain": inst.domain,
        "license_status": inst.license_status,
        "is_online": inst.is_online,
        "version": inst.version or "",
        "first_seen_at": inst.first_seen_at.isoformat() if inst.first_seen_at else None,
        "last_heartbeat_at": inst.last_heartbeat_at.isoformat() if inst.last_heartbeat_at else None,
        "ip_address": inst.ip_address or "",
        "active_screens": last_usage.active_screens if last_usage else None,
        "templates_count": last_usage.templates_count if last_usage else None,
        "users_count": last_usage.users_count if last_usage else None,
        "storage_used_mb": last_usage.storage_used_mb if last_usage else None,
        "usage_reported_at": last_usage.reported_at.isoformat() if last_usage else None,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDeveloper])
def gateway_instance_list(request):
    if not _saas_and_gateway():
        return Response({"detail": "Gateway admin API is not enabled."}, status=403)

    try:
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(200, max(1, int(request.query_params.get("page_size", 50))))
    except (TypeError, ValueError):
        page, page_size = 1, 50

    qs = InstanceRegistry.objects.order_by("-last_heartbeat_at", "-first_seen_at")
    total = qs.count()
    start = (page - 1) * page_size
    slice_ids = list(qs.values_list("id", flat=True)[start : start + page_size])

    instances = {str(i.id): i for i in InstanceRegistry.objects.filter(id__in=slice_ids)}
    ordered = [instances[str(i)] for i in slice_ids if str(i) in instances]

    usage_map: dict[str, InstanceUsageLog] = {}
    if slice_ids:
        for u in InstanceUsageLog.objects.filter(instance_id__in=slice_ids).order_by("-reported_at"):
            sid = str(u.instance_id)
            if sid not in usage_map:
                usage_map[sid] = u

    data = [_serialize_row(inst, usage_map.get(str(inst.id))) for inst in ordered]
    return Response(
        {
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDeveloper])
def gateway_instance_detail(request, pk):
    if not _saas_and_gateway():
        return Response({"detail": "Gateway admin API is not enabled."}, status=403)

    inst = get_object_or_404(InstanceRegistry, pk=pk)
    last_usage = (
        InstanceUsageLog.objects.filter(instance=inst).order_by("-reported_at").first()
    )
    return Response(_serialize_row(inst, last_usage))


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDeveloper])
def gateway_instance_usage(request, pk):
    if not _saas_and_gateway():
        return Response({"detail": "Gateway admin API is not enabled."}, status=403)

    inst = get_object_or_404(InstanceRegistry, pk=pk)
    try:
        limit = min(500, max(1, int(request.query_params.get("limit", 100))))
    except (TypeError, ValueError):
        limit = 100

    rows = InstanceUsageLog.objects.filter(instance=inst).order_by("-reported_at")[:limit]
    return Response(
        {
            "instance_id": str(inst.id),
            "results": [
                {
                    "reported_at": r.reported_at.isoformat(),
                    "active_screens": r.active_screens,
                    "templates_count": r.templates_count,
                    "storage_used_mb": r.storage_used_mb,
                    "commands_sent": r.commands_sent,
                    "users_count": r.users_count,
                    "extra_data": r.extra_data,
                }
                for r in rows
            ],
        }
    )
