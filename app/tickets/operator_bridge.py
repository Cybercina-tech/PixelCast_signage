"""
Push local tickets to the operator license gateway (super-admin queue on SaaS).

Only active when DEPLOYMENT_MODE=self_hosted and TICKET_OPERATOR_BRIDGE_ENABLED.
"""
from __future__ import annotations

import logging
import uuid

from django.conf import settings

from core.deployment import normalize_deployment_mode

logger = logging.getLogger(__name__)


def bridge_enabled() -> bool:
    if normalize_deployment_mode(getattr(settings, "DEPLOYMENT_MODE", None)) != "self_hosted":
        return False
    return bool(getattr(settings, "TICKET_OPERATOR_BRIDGE_ENABLED", False))


def push_new_ticket_if_configured(ticket_id: uuid.UUID) -> None:
    if not bridge_enabled():
        return
    from licensing.client import LicenseServerError, license_gateway_base_url, post_gateway_ticket_ingest
    from licensing.service import get_or_create_state

    base = license_gateway_base_url()
    state = get_or_create_state()
    token = (state.activation_token or "").strip()
    domain = (state.activated_domain or "").strip()
    if not base or not token:
        logger.debug("Ticket bridge skipped: missing LICENSE_GATEWAY_BASE_URL or activation token")
        return

    from tickets.models import Ticket

    try:
        ticket = Ticket.objects.select_related("requester").get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return

    first = (
        ticket.messages.filter(is_internal=False)
        .order_by("created_at")
        .first()
    )
    body = (first.body if first else "") or ""
    req = ticket.requester
    payload = {
        "remote_ticket_id": str(ticket.id),
        "subject": ticket.subject,
        "body": body,
        "priority": ticket.priority,
        "category": ticket.category or "",
        "language": ticket.language or "en",
        "requester_name": ((req.full_name or req.username) if req else "")[:255],
        "requester_email": (req.email if req else "")[:254],
        "client_version": (ticket.client_version or getattr(settings, "SCREENGRAM_APP_VERSION", "") or "")[
            :64
        ],
        "domain": domain,
        "app_version": (getattr(settings, "SCREENGRAM_APP_VERSION", None) or "").strip(),
    }
    try:
        post_gateway_ticket_ingest(base, token, body=payload)
    except LicenseServerError as exc:
        logger.warning("Ticket bridge ingest failed for %s: %s", ticket_id, exc)


def push_customer_reply_if_configured(ticket_id: uuid.UUID, body: str) -> None:
    if not bridge_enabled():
        return
    from licensing.client import LicenseServerError, license_gateway_base_url, post_gateway_ticket_ingest
    from licensing.service import get_or_create_state

    base = license_gateway_base_url()
    state = get_or_create_state()
    token = (state.activation_token or "").strip()
    domain = (state.activated_domain or "").strip()
    if not base or not token:
        return

    text = (body or "").strip()
    if not text:
        return

    payload = {
        "remote_ticket_id": str(ticket_id),
        "body": text,
        "domain": domain,
        "app_version": (getattr(settings, "SCREENGRAM_APP_VERSION", None) or "").strip(),
    }
    try:
        post_gateway_ticket_ingest(base, token, body=payload)
    except LicenseServerError as exc:
        logger.warning("Ticket bridge reply failed for %s: %s", ticket_id, exc)
