"""
Central license registry logic (SaaS-only). Self-hosted instances call these via HTTP.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .envato import EnvatoApiError, fetch_sale_by_purchase_code, parse_sale_item_id
from .models import (
    LicenseRegistryHeartbeatLog,
    LicenseRegistryInstallation,
    LicenseRegistryPurchase,
)

def purchase_code_fingerprint(code: str) -> str:
    normalized = (code or "").strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def hash_activation_token(token: str) -> str:
    return hashlib.sha256((token or "").encode("utf-8")).hexdigest()


def registry_enabled() -> bool:
    return bool(getattr(settings, "PLATFORM_SAAS_ENABLED", False)) and bool(
        getattr(settings, "LICENSE_REGISTRY_API_ENABLED", True)
    )


def envato_configured() -> bool:
    return bool((getattr(settings, "CODECANYON_TOKEN", None) or "").strip())


def expected_envato_item_ids() -> set[str]:
    raw = (getattr(settings, "CODECANYON_PRODUCT_ID", None) or "").strip()
    if not raw:
        return set()
    return {x.strip() for x in raw.split(",") if x.strip()}


def item_id_allowed(item_id: int | None) -> bool:
    allowed = expected_envato_item_ids()
    if not allowed:
        return True
    if item_id is None:
        return False
    return str(item_id) in allowed


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, timezone.datetime):
        return value if timezone.is_aware(value) else timezone.make_aware(value)
    try:
        from dateutil import parser as date_parser

        dt = date_parser.isoparse(str(value))
        return dt if timezone.is_aware(dt) else timezone.make_aware(dt)
    except Exception:
        return None


def _mark_suspicious_siblings(purchase: LicenseRegistryPurchase, domain: str) -> None:
    qs = LicenseRegistryInstallation.objects.filter(purchase=purchase).exclude(domain=domain)
    if qs.exists():
        LicenseRegistryInstallation.objects.filter(purchase=purchase).update(suspicious=True)


@transaction.atomic
def activate_installation(
    purchase_code: str,
    domain: str,
    product_id: str = "",
    app_version: str = "",
    client_ip: str | None = None,
) -> tuple[LicenseRegistryInstallation, str, dict]:
    """
    Verify with Envato, upsert purchase + installation, return (installation, plaintext_token, response_extra).
    """
    if not registry_enabled():
        raise PermissionError("License registry API is disabled")
    if not envato_configured():
        raise EnvatoApiError("License gateway is not configured (missing CODECANYON_TOKEN)", status_code=503)

    domain = (domain or "").strip().lower()
    if not domain:
        raise ValueError("domain is required")

    sale = fetch_sale_by_purchase_code(purchase_code)
    item_id = parse_sale_item_id(sale)
    if not item_id_allowed(item_id):
        raise ValueError("This purchase is not for a permitted Envato item ID")

    pid = (product_id or "").strip()
    if pid and item_id is not None and str(item_id) != pid:
        raise ValueError("Purchase code does not match the configured product ID")

    fingerprint = purchase_code_fingerprint(purchase_code)
    buyer = (sale.get("buyer") or sale.get("buyer_username") or "") if isinstance(sale, dict) else ""
    if isinstance(buyer, dict):
        buyer = buyer.get("username") or buyer.get("name") or ""

    purchase, _ = LicenseRegistryPurchase.objects.update_or_create(
        code_fingerprint=fingerprint,
        defaults={
            "envato_item_id": item_id,
            "buyer_username": str(buyer)[:191] if buyer else "",
            "sold_at": _parse_dt(sale.get("sold_at")),
            "support_until": _parse_dt(sale.get("support_until")),
            "license_type": str(sale.get("license") or "")[:64],
            "raw_sale": sale if isinstance(sale, dict) else {},
        },
    )

    _mark_suspicious_siblings(purchase, domain)

    token = secrets.token_urlsafe(48)
    th = hash_activation_token(token)

    existing = LicenseRegistryInstallation.objects.select_for_update().filter(
        purchase=purchase, domain=domain
    ).first()

    if existing:
        existing.token_hash = th
        existing.app_version = (app_version or "")[:128]
        existing.last_heartbeat_at = timezone.now()
        existing.suspended = False
        existing.suspended_reason = ""
        existing.save(
            update_fields=[
                "token_hash",
                "app_version",
                "last_heartbeat_at",
                "suspended",
                "suspended_reason",
                "updated_at",
            ]
        )
        inst = existing
    else:
        inst = LicenseRegistryInstallation.objects.create(
            purchase=purchase,
            domain=domain,
            token_hash=th,
            app_version=(app_version or "")[:128],
            last_heartbeat_at=timezone.now(),
        )

    LicenseRegistryHeartbeatLog.objects.create(
        installation=inst,
        app_version=(app_version or "")[:128],
        ip_address=client_ip or None,
    )

    extra = {
        "buyer_username": purchase.buyer_username,
        "envato_item_id": purchase.envato_item_id,
        "registry_status": compute_display_status(inst),
    }
    return inst, token, extra


def record_heartbeat(
    token: str,
    domain: str,
    app_version: str = "",
    client_ip: str | None = None,
) -> LicenseRegistryInstallation:
    if not registry_enabled():
        raise PermissionError("License registry API is disabled")

    th = hash_activation_token(token)
    try:
        inst = LicenseRegistryInstallation.objects.select_related("purchase").get(token_hash=th)
    except LicenseRegistryInstallation.DoesNotExist as exc:
        raise LookupError("Unknown activation token") from exc

    domain = (domain or "").strip().lower()
    if domain and inst.domain != domain:
        inst.suspicious = True
        _mark_suspicious_siblings(inst.purchase, domain)

    inst.last_heartbeat_at = timezone.now()
    if app_version:
        inst.app_version = app_version[:128]
    inst.save(update_fields=["last_heartbeat_at", "app_version", "suspicious", "updated_at"])

    LicenseRegistryHeartbeatLog.objects.create(
        installation=inst,
        app_version=(app_version or "")[:128],
        ip_address=client_ip or None,
    )
    return inst


def validate_by_token(token: str, domain: str | None = None) -> tuple[bool, dict]:
    """
    Return (is_valid, payload_dict) for self-hosted validate call.
    """
    if not registry_enabled():
        return False, {"valid": False, "status": "invalid", "message": "Registry disabled"}

    th = hash_activation_token(token)
    try:
        inst = LicenseRegistryInstallation.objects.select_related("purchase").get(token_hash=th)
    except LicenseRegistryInstallation.DoesNotExist:
        return False, {"valid": False, "status": "invalid", "message": "Unknown activation token"}

    if inst.suspended:
        return False, {"valid": False, "status": "suspended", "message": "License suspended by operator"}

    if domain and (domain or "").strip().lower() != inst.domain:
        return False, {"valid": False, "status": "invalid", "message": "Domain mismatch"}

    max_age = int(getattr(settings, "LICENSE_REGISTRY_HEARTBEAT_MAX_AGE_HOURS", 0) or 0)
    if max_age > 0 and inst.last_heartbeat_at:
        cutoff = timezone.now() - timedelta(hours=max_age)
        if inst.last_heartbeat_at < cutoff:
            return False, {
                "valid": False,
                "status": "inactive",
                "message": "No recent heartbeat; renew contact with license gateway",
            }

    derived = compute_display_status(inst)
    return True, {
        "valid": True,
        "status": "active" if derived == LicenseRegistryInstallation.STATUS_ACTIVE else derived,
        "license_status": derived,
        "message": "OK",
    }


def compute_display_status(inst: LicenseRegistryInstallation) -> str:
    if inst.suspended:
        return LicenseRegistryInstallation.STATUS_SUSPENDED
    if inst.suspicious:
        return LicenseRegistryInstallation.STATUS_SUSPICIOUS

    inactive_hours = int(getattr(settings, "LICENSE_REGISTRY_INACTIVE_AFTER_HOURS", 72) or 72)
    now = timezone.now()
    last = inst.last_heartbeat_at
    if not last:
        return LicenseRegistryInstallation.STATUS_PENDING
    if last < now - timedelta(hours=inactive_hours):
        return LicenseRegistryInstallation.STATUS_INACTIVE
    return LicenseRegistryInstallation.STATUS_ACTIVE


def validate_legacy_purchase_body(
    purchase_code: str,
    domain: str,
    product_id: str = "",
) -> tuple[bool, dict]:
    """
    Expensive path: verify purchase code with Envato on each call (legacy self-hosted client).
    """
    if not registry_enabled():
        return False, {"valid": False, "status": "invalid", "message": "Registry disabled"}
    if not envato_configured():
        return False, {"valid": False, "status": "invalid", "message": "Gateway not configured"}

    try:
        sale = fetch_sale_by_purchase_code(purchase_code)
    except EnvatoApiError as exc:
        return False, {"valid": False, "status": "invalid", "message": str(exc)}

    item_id = parse_sale_item_id(sale)
    if not item_id_allowed(item_id):
        return False, {"valid": False, "status": "invalid", "message": "Item not permitted"}

    pid = (product_id or "").strip()
    if pid and item_id is not None and str(item_id) != pid:
        return False, {"valid": False, "status": "invalid", "message": "Product mismatch"}

    return True, {"valid": True, "status": "active", "message": "OK", "domain": (domain or "").strip()}
