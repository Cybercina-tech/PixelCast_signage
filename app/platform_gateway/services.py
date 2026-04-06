from __future__ import annotations

import logging
import secrets
from urllib.parse import urlparse

from django.conf import settings
from django.db import transaction
from licensing.envato import EnvatoApiError, fetch_sale_by_purchase_code, parse_sale_item_id
from licensing.registry_service import item_id_allowed, purchase_code_fingerprint

from .models import InstanceRegistry
from .utils import hash_api_key

logger = logging.getLogger(__name__)


def normalize_domain(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    # Accept with or without scheme; store normalized host + scheme if present
    if "://" not in s:
        s = "https://" + s
    parsed = urlparse(s)
    host = (parsed.netloc or parsed.path or "").strip().lower().rstrip("/")
    if not host:
        return ""
    scheme = (parsed.scheme or "https").lower()
    if scheme not in ("http", "https"):
        scheme = "https"
    return f"{scheme}://{host}"


def validate_purchase_code(purchase_code: str) -> dict:
    """
    Verify purchase with Envato; return sale dict or raise EnvatoApiError.
    """
    sale = fetch_sale_by_purchase_code(purchase_code)
    item_id = parse_sale_item_id(sale)
    if not item_id_allowed(item_id):
        raise EnvatoApiError("Purchase item is not allowed for this product", status_code=403)
    return sale


@transaction.atomic
def register_new_instance(*, purchase_code: str, domain: str, version: str, client_ip: str | None):
    """
    If purchase fingerprint already registered: returns ("conflict", existing_instance, None).
    Else validates with Envato and returns ("created", new_instance, raw_api_key_once).
    """
    fp = purchase_code_fingerprint(purchase_code)
    existing = InstanceRegistry.objects.filter(purchase_code_fingerprint=fp).first()
    if existing:
        return "conflict", existing, None

    validate_purchase_code(purchase_code)
    dom = normalize_domain(domain)
    if not dom:
        raise ValueError("domain is required")

    raw_key = secrets.token_urlsafe(32)
    key_hash = hash_api_key(raw_key)

    inst = InstanceRegistry.objects.create(
        purchase_code_fingerprint=fp,
        domain=dom[:255],
        ip_address=client_ip or None,
        api_key_hash=key_hash,
        version=(version or "")[:20],
        metadata={},
    )
    return "created", inst, raw_key


def gateway_public_enabled() -> bool:
    if not getattr(settings, "PLATFORM_GATEWAY_ENABLED", False):
        return False
    if not getattr(settings, "PLATFORM_SAAS_ENABLED", False):
        return False
    return True
