"""Self-serve Stripe Checkout and Customer Portal for tenant admins."""

from __future__ import annotations

import logging

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import RolePermissions

from .pricing_checkout import resolve_checkout_for_plan
from .pricing_models import BillingPromotion, PlatformBillingSettings, SubscriptionPlan

logger = logging.getLogger(__name__)


def _saas_enabled():
    return bool(getattr(settings, 'PLATFORM_SAAS_ENABLED', False))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """POST /api/platform/billing/checkout-session/ — Stripe Checkout for subscription."""
    if not _saas_enabled():
        return Response({'detail': 'SaaS billing is not enabled.'}, status=status.HTTP_403_FORBIDDEN)
    if not RolePermissions.can_manage_all(request.user) and not request.user.is_manager():
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
    tenant = getattr(request.user, 'tenant', None)
    if not tenant:
        return Response({'detail': 'No tenant on account.'}, status=status.HTTP_400_BAD_REQUEST)

    secret = (getattr(settings, 'STRIPE_SECRET_KEY', '') or '').strip()
    if not secret:
        return Response({'detail': 'Stripe is not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        import stripe
    except ImportError:
        return Response({'detail': 'stripe package not installed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    stripe.api_key = secret
    base = getattr(settings, 'PUBLIC_WEB_APP_URL', 'http://localhost:5173').rstrip('/')
    success_url = request.data.get('success_url') or f'{base}/settings?billing=1'
    cancel_url = request.data.get('cancel_url') or f'{base}/settings?billing=cancel'

    plan_key = (request.data.get('plan_key') or '').strip()
    quantity_raw = request.data.get('quantity')
    quantity = None
    if quantity_raw is not None:
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            return Response({'detail': 'Invalid quantity.'}, status=status.HTTP_400_BAD_REQUEST)

    promotion_row_id = request.data.get('promotion_id')

    solo = PlatformBillingSettings.get_solo()
    allow_promo = solo.checkout_allow_promotion_codes

    try:
        if plan_key:
            plan = SubscriptionPlan.objects.filter(key=plan_key, is_active=True).first()
            if not plan:
                return Response({'detail': 'Unknown or inactive plan.'}, status=status.HTTP_400_BAD_REQUEST)
            resolved = resolve_checkout_for_plan(plan, quantity)
            line_items = resolved.line_items
            meta_device_limit = resolved.device_limit_meta
            meta_plan_key = resolved.plan_key
        else:
            # Legacy single-price checkout
            price = (getattr(settings, 'STRIPE_PRICE_ID', '') or '').strip()
            if not price:
                return Response(
                    {'detail': 'Pass plan_key or set STRIPE_PRICE_ID for legacy checkout.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            line_items = [{'price': price, 'quantity': 1}]
            meta_device_limit = ''
            meta_plan_key = 'legacy'

        if not tenant.stripe_customer_id:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=tenant.name,
                metadata={'tenant_id': str(tenant.id)},
            )
            tenant.stripe_customer_id = customer.id
            tenant.save(update_fields=['stripe_customer_id', 'updated_at'])

        subscription_metadata = {
            'tenant_id': str(tenant.id),
            'plan_key': meta_plan_key,
        }
        if meta_device_limit:
            subscription_metadata['device_limit'] = meta_device_limit

        session_kw: dict = {
            'mode': 'subscription',
            'customer': tenant.stripe_customer_id,
            'line_items': line_items,
            'success_url': success_url + ('&' if '?' in success_url else '?') + 'session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': cancel_url,
            'subscription_data': {'metadata': subscription_metadata},
            'metadata': {
                'tenant_id': str(tenant.id),
                'plan_key': meta_plan_key,
            },
        }

        applied_discount = False
        if promotion_row_id:
            try:
                pid = int(promotion_row_id)
            except (TypeError, ValueError):
                return Response({'detail': 'Invalid promotion_id.'}, status=status.HTTP_400_BAD_REQUEST)
            promo = BillingPromotion.objects.filter(pk=pid, is_active=True).first()
            if promo:
                session_kw['discounts'] = [{'promotion_code': promo.stripe_promotion_code_id}]
                applied_discount = True

        # Stripe: do not combine customer-entered promo codes with preset discounts on the same session.
        if allow_promo and not applied_discount:
            session_kw['allow_promotion_codes'] = True

        session = stripe.checkout.Session.create(**session_kw)
        return Response({'url': session.url, 'id': session.id})
    except ValidationError as e:
        return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception('checkout session: %s', e)
        return Response({'detail': str(e)[:500]}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_billing_portal_session(request):
    """POST /api/platform/billing/portal-session/ — Stripe Customer Portal."""
    if not _saas_enabled():
        return Response({'detail': 'SaaS billing is not enabled.'}, status=status.HTTP_403_FORBIDDEN)
    if not (RolePermissions.can_manage_all(request.user) or request.user.is_manager()):
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
    tenant = getattr(request.user, 'tenant', None)
    if not tenant or not tenant.stripe_customer_id:
        return Response({'detail': 'No Stripe customer for this tenant.'}, status=status.HTTP_400_BAD_REQUEST)
    secret = (getattr(settings, 'STRIPE_SECRET_KEY', '') or '').strip()
    if not secret:
        return Response({'detail': 'Stripe is not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    try:
        import stripe
    except ImportError:
        return Response({'detail': 'stripe package not installed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    stripe.api_key = secret
    base = getattr(settings, 'PUBLIC_WEB_APP_URL', 'http://localhost:5173').rstrip('/')
    return_url = request.data.get('return_url') or f'{base}/settings'
    try:
        portal = stripe.billing_portal.Session.create(
            customer=tenant.stripe_customer_id,
            return_url=return_url,
        )
        return Response({'url': portal.url})
    except Exception as e:
        logger.exception('portal session: %s', e)
        return Response({'detail': str(e)[:500]}, status=status.HTTP_502_BAD_GATEWAY)
