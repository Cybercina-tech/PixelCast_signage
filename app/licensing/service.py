import logging
import re
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .client import (
    LicenseServerError,
    license_gateway_base_url,
    license_validate_url,
    post_gateway_activate,
    post_license_validation,
)
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

    st = str(data.get("status", "") or data.get("license_status", "")).lower()
    if st in {"invalid", "expired", "revoked", "suspended", "inactive"}:
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


def _masked_token_preview(token: str) -> str:
    t = (token or "").strip()
    if len(t) <= 12:
        return "****" if t else ""
    return f"{t[:4]}…{t[-4:]}"


def activate_license(purchase_code: str, domain: str = "", override_product_id: str = ""):
    state = get_or_create_state()
    code = (purchase_code or "").strip()
    if override_product_id is not None:
        state.codecanyon_product_id_override = (override_product_id or "").strip()
    if domain:
        state.activated_domain = domain.strip()
    state.activated_at = timezone.now()
    state.license_status = LicenseState.STATUS_INACTIVE
    state.last_error = ""
    cache.delete(_cache_key())

    base = license_gateway_base_url()
    if base:
        if not _purchase_code_shape_valid(code):
            state.last_error = "Purchase code format is invalid"
            state.touch_signature()
            state.save()
            return LicenseDecision(
                allow=False,
                status=LicenseState.STATUS_INVALID,
                error_code="license_invalid",
                message="Purchase code format is invalid",
            )

        product_id, _ = resolve_product_id(state)
        app_version = (getattr(settings, "SCREENGRAM_APP_VERSION", "") or "").strip()
        try:
            data = post_gateway_activate(
                base,
                {
                    "purchase_code": code,
                    "domain": state.activated_domain or "",
                    "product_id": product_id,
                    "app_version": app_version,
                },
            )
        except LicenseServerError as exc:
            logger.warning("License gateway activation failed: %s", exc)
            state.purchase_code = code
            state.activation_token = ""
            state.last_error = str(exc)
            state.touch_signature()
            state.save()
            return LicenseDecision(
                allow=False,
                status=LicenseState.STATUS_INACTIVE,
                error_code="license_activation_failed",
                message=str(exc),
            )

        token = (data.get("activation_token") or "").strip()
        if not token:
            state.purchase_code = code
            state.activation_token = ""
            state.last_error = data.get("message") or "Gateway did not return an activation token"
            state.touch_signature()
            state.save()
            return LicenseDecision(
                allow=False,
                status=LicenseState.STATUS_INACTIVE,
                error_code="license_activation_failed",
                message=state.last_error,
            )

        state.purchase_code = ""
        state.activation_token = token
        state.last_error = ""
        state.touch_signature()
        state.save()
        return validate_license(force=True)

    state.purchase_code = code
    state.activation_token = ""
    state.touch_signature()
    state.save()
    return validate_license(force=True)


def current_status_payload():
    state = get_or_create_state()
    product_id, source = resolve_product_id(state)
    gw = bool(license_gateway_base_url())
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
        "license_gateway_configured": gw,
        "uses_activation_token": bool((state.activation_token or "").strip()),
        "masked_activation_token": _masked_token_preview(state.activation_token),
        "masked_purchase_code": state.masked_purchase_code(),
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
    token_secret = (state.activation_token or "").strip()
    purchase = (state.purchase_code or "").strip()

    if not token_secret and not purchase:
        state.license_status = LicenseState.STATUS_INACTIVE
        state.last_error = "Purchase code or activation token is not set"
        state.last_validation_at = now
        state.touch_signature()
        state.save(
            update_fields=[
                "license_status",
                "last_error",
                "last_validation_at",
                "validation_signature",
                "updated_at",
            ]
        )
        decision = LicenseDecision(
            allow=False,
            status=state.license_status,
            error_code="license_required",
            message="Activate your license with a purchase code",
        )
        cache.set(_cache_key(), decision, cache_ttl)
        return decision

    timeout_seconds = int(getattr(settings, "LICENSE_SERVER_TIMEOUT_SECONDS", 8))
    app_version = (getattr(settings, "SCREENGRAM_APP_VERSION", "") or "").strip()

    try:
        if token_secret:
            vurl = license_validate_url()
            if not vurl:
                raise LicenseServerError("LICENSE_GATEWAY_BASE_URL or LICENSE_SERVER_URL is not configured")

            is_valid, data = post_license_validation(
                license_server_url=vurl,
                payload={
                    "domain": state.activated_domain or "",
                    "app_version": app_version,
                },
                auth_bearer=token_secret,
                timeout_seconds=timeout_seconds,
            )
            product_source = "gateway_token"
        else:
            if not _purchase_code_shape_valid(purchase):
                state.license_status = LicenseState.STATUS_INVALID
                state.last_error = "Purchase code format is invalid"
                state.last_validation_at = now
                state.touch_signature()
                state.save(
                    update_fields=[
                        "license_status",
                        "last_error",
                        "last_validation_at",
                        "validation_signature",
                        "updated_at",
                    ]
                )
                decision = LicenseDecision(
                    allow=False,
                    status=state.license_status,
                    error_code="license_invalid",
                    message="Purchase code format is invalid",
                )
                cache.set(_cache_key(), decision, cache_ttl)
                return decision

            payload, product_source = _build_payload(state)
            codecanyon_token = getattr(settings, "CODECANYON_TOKEN", "")
            url = license_validate_url()
            if not url:
                raise LicenseServerError("LICENSE_SERVER_URL is not configured")

            is_valid, data = post_license_validation(
                license_server_url=url,
                payload=payload,
                token=codecanyon_token,
                timeout_seconds=timeout_seconds,
            )

        mapped_status = _normalize_status(is_valid, data)
        state.license_status = mapped_status
        state.last_validation_at = now
        state.last_error = ""

        if mapped_status == LicenseState.STATUS_ACTIVE:
            state.last_successful_validation_at = now
            state.grace_until = now + timedelta(hours=grace_hours)
            dom = (data.get("domain") or "").strip()
            if not state.activated_domain and dom:
                state.activated_domain = dom
        else:
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
