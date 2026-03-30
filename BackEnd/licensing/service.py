import logging
import re
from datetime import timedelta
from dataclasses import dataclass
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .client import LicenseServerError, post_license_validation
from .models import LicenseState


logger = logging.getLogger(__name__)
PURCHASE_CODE_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


@dataclass
class LicenseDecision:
    allow: bool
    status: str
    error_code: str
    message: str
    grace_until: object = None


def _cache_key() -> str:
    return "licensing:decision:v1"


def resolve_product_id(state: LicenseState):
    env_product_id = (getattr(settings, "CODECANYON_PRODUCT_ID", "") or "").strip()
    if env_product_id:
        return env_product_id, "env"

    db_product_id = (state.codecanyon_product_id_override or "").strip()
    if db_product_id:
        return db_product_id, "db"

    return "", "temporary"


def _purchase_code_shape_valid(code: str) -> bool:
    return bool(PURCHASE_CODE_RE.match((code or "").strip()))


def _normalize_status(is_valid: bool, data: dict) -> str:
    if is_valid:
        return LicenseState.STATUS_ACTIVE

    if str(data.get("status", "")).lower() in {"invalid", "expired", "revoked"}:
        return LicenseState.STATUS_INVALID

    return LicenseState.STATUS_INVALID


def _build_payload(state: LicenseState):
    product_id, product_source = resolve_product_id(state)
    payload = {
        "purchase_code": state.purchase_code,
        "product_id": product_id,
        "domain": state.activated_domain,
    }
    return payload, product_source


def get_or_create_state() -> LicenseState:
    return LicenseState.get_solo()


def activate_license(purchase_code: str, domain: str = "", override_product_id: str = ""):
    state = get_or_create_state()
    state.purchase_code = (purchase_code or "").strip()
    if domain:
        state.activated_domain = domain.strip()
    if override_product_id is not None:
        state.codecanyon_product_id_override = (override_product_id or "").strip()
    state.activated_at = timezone.now()
    state.license_status = LicenseState.STATUS_INACTIVE
    state.last_error = ""
    state.touch_signature()
    state.save()
    cache.delete(_cache_key())
    return validate_license(force=True)


def current_status_payload():
    state = get_or_create_state()
    product_id, source = resolve_product_id(state)
    return {
        "status": "success",
        "message": "License status fetched",
        "license_status": state.license_status,
        "grace_until": state.grace_until,
        "activated_domain": state.activated_domain,
        "product_id": product_id,
        "product_id_source": source,
        "last_validation_at": state.last_validation_at,
        "last_successful_validation_at": state.last_successful_validation_at,
        "enforcement_enabled": bool(
            getattr(settings, "LICENSE_ENFORCEMENT_ENABLED", False)
        ),
    }


def validate_license(force: bool = False) -> LicenseDecision:
    cache_ttl = int(getattr(settings, "LICENSE_CACHE_TTL_SECONDS", 900))
    grace_hours = int(getattr(settings, "LICENSE_OFFLINE_GRACE_HOURS", 72))

    if not force:
        cached = cache.get(_cache_key())
        if cached:
            return cached

    state = get_or_create_state()
    now = timezone.now()

    if not state.purchase_code:
        state.license_status = LicenseState.STATUS_INACTIVE
        state.last_error = "Purchase code is not set"
        state.last_validation_at = now
        state.touch_signature()
        state.save(update_fields=["license_status", "last_error", "last_validation_at", "validation_signature", "updated_at"])
        decision = LicenseDecision(
            allow=False,
            status=state.license_status,
            error_code="license_required",
            message="Purchase code is required",
        )
        cache.set(_cache_key(), decision, cache_ttl)
        return decision

    if not _purchase_code_shape_valid(state.purchase_code):
        state.license_status = LicenseState.STATUS_INVALID
        state.last_error = "Purchase code format is invalid"
        state.last_validation_at = now
        state.touch_signature()
        state.save(update_fields=["license_status", "last_error", "last_validation_at", "validation_signature", "updated_at"])
        decision = LicenseDecision(
            allow=False,
            status=state.license_status,
            error_code="license_invalid",
            message="Purchase code format is invalid",
        )
        cache.set(_cache_key(), decision, cache_ttl)
        return decision

    payload, product_source = _build_payload(state)
    token = getattr(settings, "CODECANYON_TOKEN", "")
    url = getattr(settings, "LICENSE_SERVER_URL", "")
    timeout_seconds = int(getattr(settings, "LICENSE_SERVER_TIMEOUT_SECONDS", 8))

    try:
        is_valid, data = post_license_validation(
            license_server_url=url,
            payload=payload,
            token=token,
            timeout_seconds=timeout_seconds,
        )
        mapped_status = _normalize_status(is_valid, data)
        state.license_status = mapped_status
        state.last_validation_at = now
        state.last_error = ""

        if mapped_status == LicenseState.STATUS_ACTIVE:
            state.last_successful_validation_at = now
            state.grace_until = now + timedelta(hours=grace_hours)
            if not state.activated_domain and payload.get("domain"):
                state.activated_domain = payload.get("domain")
        else:
            # hard-fail if server explicitly invalidated it
            state.grace_until = now

        state.touch_signature()
        state.save()

        if mapped_status == LicenseState.STATUS_ACTIVE:
            decision = LicenseDecision(
                allow=True,
                status=mapped_status,
                error_code="",
                message=f"License is active ({product_source})",
                grace_until=state.grace_until,
            )
        else:
            decision = LicenseDecision(
                allow=False,
                status=mapped_status,
                error_code="license_invalid",
                message=data.get("message", "License is invalid"),
                grace_until=state.grace_until,
            )

        cache.set(_cache_key(), decision, cache_ttl)
        return decision

    except LicenseServerError as exc:
        logger.warning("License server unavailable: %s", exc)
        state.last_validation_at = now
        state.last_error = str(exc)

        if state.last_successful_validation_at:
            grace_until = state.last_successful_validation_at + timedelta(hours=grace_hours)
            state.grace_until = grace_until
            if now <= grace_until:
                state.license_status = LicenseState.STATUS_GRACE
                state.touch_signature()
                state.save(
                    update_fields=[
                        "license_status",
                        "last_validation_at",
                        "last_error",
                        "grace_until",
                        "validation_signature",
                        "updated_at",
                    ]
                )
                decision = LicenseDecision(
                    allow=True,
                    status=LicenseState.STATUS_GRACE,
                    error_code="",
                    message="License server unavailable; running in grace mode",
                    grace_until=grace_until,
                )
                cache.set(_cache_key(), decision, cache_ttl)
                return decision

        state.license_status = LicenseState.STATUS_INVALID
        state.touch_signature()
        state.save(
            update_fields=[
                "license_status",
                "last_validation_at",
                "last_error",
                "validation_signature",
                "updated_at",
            ]
        )
        decision = LicenseDecision(
            allow=False,
            status=state.license_status,
            error_code="grace_expired",
            message="License server unavailable and grace period has expired",
            grace_until=state.grace_until,
        )
        cache.set(_cache_key(), decision, cache_ttl)
        return decision
