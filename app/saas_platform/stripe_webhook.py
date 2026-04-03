"""Stripe webhook handler (signature-verified)."""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import BillingWebhookEvent, Tenant
from .services import (
    apply_payment_failed,
    find_tenant_by_stripe_customer,
    sync_tenant_from_stripe_subscription,
    upsert_invoice_from_stripe,
)

logger = logging.getLogger(__name__)


def _get_tenant_from_event(obj: dict[str, Any]) -> Tenant | None:
    cid = None
    if obj.get('object') == 'customer':
        cid = obj.get('id')
    else:
        cid = obj.get('customer')
    if isinstance(cid, dict):
        cid = cid.get('id')
    return find_tenant_by_stripe_customer(cid) if cid else None


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    if not getattr(settings, 'PLATFORM_SAAS_ENABLED', False):
        return HttpResponse(status=404)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '') or ''

    try:
        import stripe
    except ImportError:
        logger.error('stripe package not installed')
        return HttpResponse('stripe not installed', status=500)

    if not secret:
        logger.warning('STRIPE_WEBHOOK_SECRET not configured; rejecting webhook')
        return HttpResponseBadRequest('webhook not configured')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except ValueError:
        return HttpResponseBadRequest('invalid payload')
    except Exception as e:
        # stripe.error.SignatureVerificationError (package exposes this name across versions)
        if 'SignatureVerification' not in type(e).__name__:
            logger.exception('Stripe webhook construct_event failed')
            return HttpResponse('webhook handler error', status=500)
        return HttpResponseBadRequest('invalid signature')

    event_dict = event.to_dict() if hasattr(event, 'to_dict') else dict(event)
    event_id = event_dict.get('id')
    event_type = event_dict.get('type') or ''

    if BillingWebhookEvent.objects.filter(stripe_event_id=event_id).exists():
        return HttpResponse(status=200)

    data_object = (event_dict.get('data') or {}).get('object') or {}
    tenant = _get_tenant_from_event(data_object)

    processed_ok = True
    err_msg = ''

    try:
        if event_type == 'customer.subscription.updated' or event_type == 'customer.subscription.deleted':
            cid = data_object.get('customer')
            if isinstance(cid, dict):
                cid = cid.get('id')
            t = find_tenant_by_stripe_customer(cid) if cid else None
            if t and event_type.endswith('deleted'):
                t.stripe_subscription_id = ''
                t.subscription_status = 'canceled'
                t.save(update_fields=['stripe_subscription_id', 'subscription_status', 'updated_at'])
            elif t:
                sync_tenant_from_stripe_subscription(t, data_object)

        elif event_type == 'invoice.payment_failed':
            t = _get_tenant_from_event(data_object)
            if t:
                apply_payment_failed(t)

        elif event_type == 'invoice.payment_succeeded':
            t = _get_tenant_from_event(data_object)
            if t:
                t.last_payment_failed_at = None
                t.payment_failed_count = 0
                t.billing_grace_until = None
                t.save(
                    update_fields=[
                        'last_payment_failed_at',
                        'payment_failed_count',
                        'billing_grace_until',
                        'updated_at',
                    ]
                )
                upsert_invoice_from_stripe(t, data_object)

        elif event_type == 'invoice.finalized' or event_type == 'invoice.paid':
            t = _get_tenant_from_event(data_object)
            if t:
                upsert_invoice_from_stripe(t, data_object)

    except Exception as e:
        processed_ok = False
        err_msg = str(e)
        logger.exception('Stripe webhook processing error: %s', e)

    BillingWebhookEvent.objects.create(
        stripe_event_id=event_id,
        event_type=event_type,
        tenant=tenant,
        payload_summary={'id': event_id, 'type': event_type},
        processed_ok=processed_ok,
        error_message=err_msg[:2000],
    )

    return HttpResponse(status=200)
