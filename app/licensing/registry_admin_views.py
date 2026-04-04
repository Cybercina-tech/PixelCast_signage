"""Super-admin (platform) API for self-hosted license registry rows."""

from __future__ import annotations

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from licensing.models import LicenseRegistryHeartbeatLog, LicenseRegistryInstallation
from licensing.registry_service import compute_display_status
from saas_platform.permissions import IsDeveloper


def _saas():
    return bool(getattr(settings, "PLATFORM_SAAS_ENABLED", False))


def _serialize_installation(inst: LicenseRegistryInstallation) -> dict:
    purchase = inst.purchase
    return {
        "id": str(inst.id),
        "domain": inst.domain,
        "app_version": inst.app_version,
        "last_heartbeat_at": inst.last_heartbeat_at.isoformat() if inst.last_heartbeat_at else None,
        "activated_at": inst.activated_at.isoformat() if inst.activated_at else None,
        "suspended": inst.suspended,
        "suspended_reason": inst.suspended_reason,
        "suspicious": inst.suspicious,
        "notes": inst.notes,
        "display_status": compute_display_status(inst),
        "purchase": {
            "code_fingerprint": purchase.code_fingerprint,
            "buyer_username": purchase.buyer_username,
            "envato_item_id": purchase.envato_item_id,
            "sold_at": purchase.sold_at.isoformat() if purchase.sold_at else None,
            "support_until": purchase.support_until.isoformat() if purchase.support_until else None,
            "license_type": purchase.license_type,
        },
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDeveloper])
def self_hosted_license_list(request):
    if not _saas():
        return Response({"detail": "SaaS not enabled."}, status=403)

    qs = LicenseRegistryInstallation.objects.select_related("purchase").order_by("-last_heartbeat_at", "-activated_at")
    data = [_serialize_installation(x) for x in qs[:200]]
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDeveloper])
def self_hosted_license_detail(request, pk):
    if not _saas():
        return Response({"detail": "SaaS not enabled."}, status=403)
    inst = get_object_or_404(LicenseRegistryInstallation.objects.select_related("purchase"), pk=pk)
    return Response(_serialize_installation(inst))


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDeveloper])
def self_hosted_license_suspend(request, pk):
    if not _saas():
        return Response({"detail": "SaaS not enabled."}, status=403)
    inst = get_object_or_404(LicenseRegistryInstallation, pk=pk)
    reason = (request.data.get("reason") or "").strip()[:2000]
    inst.suspended = True
    inst.suspended_reason = reason or "Suspended by operator"
    inst.save(update_fields=["suspended", "suspended_reason", "updated_at"])
    return Response(_serialize_installation(inst))


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDeveloper])
def self_hosted_license_reactivate(request, pk):
    if not _saas():
        return Response({"detail": "SaaS not enabled."}, status=403)
    inst = get_object_or_404(LicenseRegistryInstallation, pk=pk)
    inst.suspended = False
    inst.suspended_reason = ""
    inst.save(update_fields=["suspended", "suspended_reason", "updated_at"])
    return Response(_serialize_installation(inst))


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDeveloper])
def self_hosted_license_suspicious(request, pk):
    if not _saas():
        return Response({"detail": "SaaS not enabled."}, status=403)
    inst = get_object_or_404(LicenseRegistryInstallation, pk=pk)
    flag = request.data.get("suspicious")
    inst.suspicious = bool(flag) if flag is not None else not inst.suspicious
    inst.save(update_fields=["suspicious", "updated_at"])
    return Response(_serialize_installation(inst))


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDeveloper])
def self_hosted_license_heartbeats(request, pk):
    if not _saas():
        return Response({"detail": "SaaS not enabled."}, status=403)
    inst = get_object_or_404(LicenseRegistryInstallation, pk=pk)
    logs = LicenseRegistryHeartbeatLog.objects.filter(installation=inst).order_by("-received_at")[:100]
    return Response({
        "results": [
            {
                "id": str(l.id),
                "received_at": l.received_at.isoformat() if l.received_at else None,
                "app_version": l.app_version,
                "ip_address": l.ip_address,
            }
            for l in logs
        ]
    })
