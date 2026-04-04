"""Aggregated super-admin reports (registry + SaaS rollups)."""

from __future__ import annotations

import re
from datetime import timedelta

from django.conf import settings
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.jwt_sessions import active_session_stats_by_tenant
from licensing.models import LicenseRegistryInstallation, LicenseRegistryPurchase
from signage.models import Schedule, Screen
from templates.models import Template
from tickets.models import Ticket

from .models import Tenant
from .permissions import IsDeveloper


def _saas_enabled() -> bool:
    return bool(getattr(settings, "PLATFORM_SAAS_ENABLED", False))


def _version_tuple(v: str) -> tuple[int, ...] | None:
    s = (v or "").strip()
    if not s:
        return None
    m = re.match(r"^v?(\d+)(?:\.(\d+))?(?:\.(\d+))?", s)
    if not m:
        return None
    return tuple(int(x or 0) for x in m.groups())


def _version_lt(a: str, b: str) -> bool:
    ta, tb = _version_tuple(a), _version_tuple(b)
    if not tb:
        return False
    if not ta:
        return True
    return ta < tb


def _norm_ver_label(v: str) -> str:
    return (v or "").strip().lstrip("vV")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_reports_summary(request):
    if not _saas_enabled():
        return Response(
            {"detail": "Platform SaaS features are disabled (set PLATFORM_SAAS_ENABLED=true)."},
            status=status.HTTP_403_FORBIDDEN,
        )

    now = timezone.now()
    d1 = now - timedelta(days=1)
    d7 = now - timedelta(days=7)
    d30 = now - timedelta(days=30)
    online_cutoff = now - timedelta(minutes=15)
    inactive_hours = int(getattr(settings, "LICENSE_REGISTRY_INACTIVE_AFTER_HOURS", 72) or 72)
    stale_cutoff = now - timedelta(hours=inactive_hours)
    latest_cfg = (getattr(settings, "LICENSE_REGISTRY_LATEST_VERSION", None) or "").strip()

    inactive_days = int(request.query_params.get("inactive_days", 14) or 14)
    inactive_cutoff = now - timedelta(days=max(1, inactive_days))

    purchases_n = LicenseRegistryPurchase.objects.count()
    installations = LicenseRegistryInstallation.objects.select_related("purchase")

    inst_total = installations.count()
    hb_24h = installations.filter(last_heartbeat_at__gte=d1).count()
    hb_7d = installations.filter(last_heartbeat_at__gte=d7).count()
    hb_30d = installations.filter(last_heartbeat_at__gte=d30).count()
    online_now_installs = installations.filter(last_heartbeat_at__gte=online_cutoff).count()

    start_12m = now - timedelta(days=366)
    act_rows = (
        LicenseRegistryInstallation.objects.filter(activated_at__gte=start_12m)
        .annotate(month=TruncMonth("activated_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    activations_by_month = [
        {"month": row["month"].strftime("%Y-%m") if row["month"] else "", "count": row["count"]}
        for row in act_rows
    ]

    ver_rows = (
        LicenseRegistryInstallation.objects.exclude(app_version="")
        .values("app_version")
        .annotate(count=Count("id"))
        .order_by("-count")[:40]
    )
    version_distribution = [{"version": r["app_version"], "count": r["count"]} for r in ver_rows]

    latest_ref = latest_cfg
    if not latest_ref and ver_rows:
        best: tuple[int, ...] | None = None
        for r in ver_rows:
            t = _version_tuple(r["app_version"])
            if t and (best is None or t > best):
                best = t
                latest_ref = r["app_version"]

    ver_qs = LicenseRegistryInstallation.objects.exclude(app_version="")
    total_with_version = ver_qs.count()
    on_latest_n = 0
    behind_install_ids = []
    if latest_ref and total_with_version:
        nref = _norm_ver_label(latest_ref)
        on_latest_n = sum(
            1
            for row in ver_qs.values_list("app_version", flat=True).iterator(chunk_size=2000)
            if _norm_ver_label(row) == nref
        )
        for inst in ver_qs.filter(suspended=False).iterator(chunk_size=500):
            if _norm_ver_label(inst.app_version) == nref:
                continue
            if _version_lt(inst.app_version, latest_ref):
                if len(behind_install_ids) < 60:
                    behind_install_ids.append(
                        {
                            "id": str(inst.id),
                            "domain": inst.domain,
                            "app_version": inst.app_version,
                        }
                    )

    on_latest_pct = (
        round(on_latest_n / total_with_version * 100, 1) if latest_ref and total_with_version else None
    )

    stale_heartbeats = list(
        installations.filter(suspended=False)
        .filter(Q(last_heartbeat_at__isnull=True) | Q(last_heartbeat_at__lt=stale_cutoff))
        .order_by("last_heartbeat_at")[:40]
        .values("id", "domain", "app_version", "last_heartbeat_at")
    )
    long_inactive = list(
        installations.filter(suspended=False)
        .filter(last_heartbeat_at__lt=inactive_cutoff)
        .order_by("last_heartbeat_at")[:40]
        .values("id", "domain", "app_version", "last_heartbeat_at")
    )

    dup_purchases = list(
        LicenseRegistryPurchase.objects.annotate(n=Count("installations"))
        .filter(n__gt=1)
        .order_by("-n")[:25]
        .values("id", "buyer_username", "n")
    )

    country_rows = (
        LicenseRegistryInstallation.objects.exclude(last_reported_country="")
        .values("last_reported_country")
        .annotate(count=Count("id"))
        .order_by("-count")[:40]
    )
    country_distribution = [{"country": r["last_reported_country"], "count": r["count"]} for r in country_rows]

    tz_rows = (
        LicenseRegistryInstallation.objects.exclude(last_timezone="")
        .values("last_timezone")
        .annotate(count=Count("id"))
        .order_by("-count")[:40]
    )
    timezone_distribution = [{"timezone": r["last_timezone"], "count": r["count"]} for r in tz_rows]

    avg_telemetry_screens = LicenseRegistryInstallation.objects.filter(
        last_screen_count__isnull=False
    ).aggregate(a=Avg("last_screen_count"))["a"]
    avg_telemetry_users = LicenseRegistryInstallation.objects.filter(
        last_user_count__isnull=False
    ).aggregate(a=Avg("last_user_count"))["a"]

    tenants_total = Tenant.objects.count()
    paying_tenants = Tenant.objects.filter(
        subscription_status__in=("active", "trialing"),
    ).exclude(Q(stripe_subscription_id__isnull=True) | Q(stripe_subscription_id="")).count()

    session_stats = active_session_stats_by_tenant()
    saas_online_users = sum(int(x.get("active_user_count", 0) or 0) for x in session_stats.values())

    self_hosted_active_approx = installations.filter(
        suspended=False, last_heartbeat_at__gte=stale_cutoff
    ).count()

    unit_cents = int(getattr(settings, "LICENSE_REVENUE_ESTIMATE_UNIT_CENTS", 0) or 0)
    license_revenue_estimate_cents = purchases_n * unit_cents if unit_cents > 0 else None
    license_revenue_note = (
        None
        if license_revenue_estimate_cents is not None
        else "Set LICENSE_REVENUE_ESTIMATE_UNIT_CENTS for a simple purchase-count × unit estimate."
    )

    tenant_screen_agg = (
        Screen.objects.filter(owner__tenant__isnull=False)
        .values("owner__tenant_id")
        .annotate(n=Count("id"))
    )
    avg_screens_per_saas_tenant = tenant_screen_agg.aggregate(a=Avg("n"))["a"]

    tenant_tpl_agg = (
        Template.objects.filter(created_by__tenant__isnull=False)
        .values("created_by__tenant_id")
        .annotate(n=Count("id"))
    )
    avg_templates_per_saas_tenant = tenant_tpl_agg.aggregate(a=Avg("n"))["a"]

    usage_proxies = {
        "schedule_entities_total": Schedule.objects.count(),
        "tickets_last_30d": Ticket.objects.filter(is_deleted=False, created_at__gte=d30).count(),
        "screens_total_saas": Screen.objects.filter(owner__tenant__isnull=False).count(),
        "templates_total_saas": Template.objects.filter(created_by__tenant__isnull=False).count(),
        "note": "Feature mix (scheduling vs analytics vs helpdesk) is approximated from entity counts and tickets, not product telemetry.",
    }

    return Response(
        {
            "generated_at": now.isoformat(),
            "self_hosted": {
                "purchases_count": purchases_n,
                "installations_count": inst_total,
                "heartbeats_last_24h_installs": hb_24h,
                "heartbeats_last_7d_installs": hb_7d,
                "heartbeats_last_30d_installs": hb_30d,
                "installations_online_recent_minutes_15": online_now_installs,
                "activations_by_month": activations_by_month,
                "version_distribution": version_distribution,
                "latest_version_reference": latest_ref or None,
                "on_latest_version_pct": on_latest_pct,
                "installations_behind_latest_sample": behind_install_ids,
                "avg_reported_screens_per_install": round(avg_telemetry_screens, 2)
                if avg_telemetry_screens is not None
                else None,
                "avg_reported_users_per_install": round(avg_telemetry_users, 2)
                if avg_telemetry_users is not None
                else None,
                "inactive_hours_threshold": inactive_hours,
                "stale_heartbeat_installs": stale_heartbeats,
                "inactive_after_days": inactive_days,
                "inactive_installs_sample": long_inactive,
                "purchases_with_multiple_domains": dup_purchases,
                "country_distribution": country_distribution,
                "timezone_distribution": timezone_distribution,
            },
            "saas": {
                "tenants_total": tenants_total,
                "tenants_paying_with_subscription": paying_tenants,
                "active_online_users_sum": saas_online_users,
                "avg_screens_per_tenant": round(avg_screens_per_saas_tenant, 2)
                if avg_screens_per_saas_tenant is not None
                else None,
                "avg_templates_per_tenant": round(avg_templates_per_saas_tenant, 2)
                if avg_templates_per_saas_tenant is not None
                else None,
                "approx_active_self_hosted_installs": self_hosted_active_approx,
                "ratio_note": "Compare tenants_paying_with_subscription (SaaS) vs approx_active_self_hosted_installs (registry heartbeats).",
            },
            "revenue": {
                "license_estimate_cents": license_revenue_estimate_cents,
                "license_estimate_note": license_revenue_note,
            },
            "usage": usage_proxies,
        }
    )
