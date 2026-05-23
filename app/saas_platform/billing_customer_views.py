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

from .billing_redirect import billing_redirect_base, validate_billing_redirect_url
from .pricing_checkout import resolve_checkout_for_plan
from .pricing_models import BillingPromotion, PlatformBillingSettings, SubscriptionPlan
from .services import sync_tenant_from_stripe_subscription
from .stripe_config import get_stripe_billing_config, get_stripe_secret_key
from .tenant_assignment import ensure_user_tenant

logger = logging.getLogger(__name__)


def _saas_enabled():
    return bool(getattr(settings, 'PLATFORM_SAAS_ENABLED', False))


def _resolve_request_tenant(user):
    tenant = getattr(user, 'tenant', None)
    if tenant:
        return tenant
    ensure_user_tenant(user)
    user.refresh_from_db(fields=['tenant'])
    return getattr(user, 'tenant', None)


def _to_dict(obj):
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    if isinstance(obj, dict):
        return obj
    return dict(obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """POST /api/platform/billing/checkout-session/ — Stripe Checkout for subscription."""
    if not _saas_enabled():
        return Response({'detail': 'SaaS billing is not enabled.'}, status=status.HTTP_403_FORBIDDEN)
    if not RolePermissions.can_manage_all(request.user) and not request.user.is_manager():
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        tenant = _resolve_request_tenant(request.user)
    except Exception as e:
        logger.exception('checkout tenant bootstrap: %s', e)
        return Response({'detail': 'Could not provision tenant for this account.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not tenant:
        return Response({'detail': 'No tenant on account.'}, status=status.HTTP_400_BAD_REQUEST)

    secret = get_stripe_secret_key()
    if not secret:
        return Response({'detail': 'Stripe is not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        import stripe
    except ImportError:
        return Response({'detail': 'stripe package not installed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    stripe.api_key = secret
    base = billing_redirect_base()
    try:
        success_url = validate_billing_redirect_url(
            request.data.get('success_url') or f'{base}/settings?billing=1',
            field_name='success_url',
        )
        cancel_url = validate_billing_redirect_url(
            request.data.get('cancel_url') or f'{base}/settings?billing=cancel',
            field_name='cancel_url',
        )
    except ValueError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
            'user_id': str(request.user.id),
            'plan_key': meta_plan_key,
            'plan_kind': plan.kind if plan_key else '',
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
                'user_id': str(request.user.id),
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
def change_subscription(request):
    """POST /api/platform/billing/change-subscription/ — in-place subscription change with explicit proration."""
    if not _saas_enabled():
        return Response({'detail': 'SaaS billing is not enabled.'}, status=status.HTTP_403_FORBIDDEN)
    if not RolePermissions.can_manage_all(request.user) and not request.user.is_manager():
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        tenant = _resolve_request_tenant(request.user)
    except Exception as e:
        logger.exception('change-subscription tenant bootstrap: %s', e)
        return Response({'detail': 'Could not provision tenant for this account.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not tenant or not tenant.stripe_subscription_id:
        return Response({'detail': 'No active Stripe subscription for this tenant.'}, status=status.HTTP_400_BAD_REQUEST)

    plan_key = (request.data.get('plan_key') or '').strip()
    if not plan_key:
        return Response({'detail': 'plan_key is required.'}, status=status.HTTP_400_BAD_REQUEST)

    quantity_raw = request.data.get('quantity')
    quantity = None
    if quantity_raw is not None:
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            return Response({'detail': 'Invalid quantity.'}, status=status.HTTP_400_BAD_REQUEST)

    proration_behavior = (request.data.get('proration_behavior') or 'create_prorations').strip()
    if proration_behavior not in {'create_prorations', 'none'}:
        return Response(
            {'detail': 'proration_behavior must be "create_prorations" or "none".'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    plan = SubscriptionPlan.objects.filter(key=plan_key, is_active=True).first()
    if not plan:
        return Response({'detail': 'Unknown or inactive plan.'}, status=status.HTTP_400_BAD_REQUEST)
    if plan.kind == SubscriptionPlan.KIND_FREE:
        return Response({'detail': 'Free plan cannot be applied through subscription change.'}, status=status.HTTP_400_BAD_REQUEST)

    secret = get_stripe_secret_key()
    if not secret:
        return Response({'detail': 'Stripe is not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    try:
        import stripe
    except ImportError:
        return Response({'detail': 'stripe package not installed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    stripe.api_key = secret
    try:
        resolved = resolve_checkout_for_plan(plan, quantity)
        sub = stripe.Subscription.retrieve(
            tenant.stripe_subscription_id,
            expand=['items.data.price'],
        )
        sub_dict = _to_dict(sub)
        items = (((sub_dict.get('items') or {}).get('data')) or [])
        if not items:
            return Response({'detail': 'Subscription has no line items.'}, status=status.HTTP_400_BAD_REQUEST)
        first_item = items[0] or {}
        item_id = first_item.get('id')
        if not item_id:
            return Response({'detail': 'Subscription item id not found.'}, status=status.HTTP_400_BAD_REQUEST)

        current_meta = sub_dict.get('metadata') or {}
        next_meta = {
            **current_meta,
            'plan_key': resolved.plan_key,
            'plan_kind': plan.kind,
            'tenant_id': str(tenant.id),
            'user_id': str(request.user.id),
            'device_limit': resolved.device_limit_meta,
        }
        modified = stripe.Subscription.modify(
            tenant.stripe_subscription_id,
            items=[
                {
                    'id': item_id,
                    'price': resolved.line_items[0]['price'],
                    'quantity': resolved.line_items[0].get('quantity', 1),
                }
            ],
            proration_behavior=proration_behavior,
            metadata=next_meta,
        )
        modified_dict = _to_dict(modified)
        sync_tenant_from_stripe_subscription(tenant, modified_dict)
        tenant.refresh_from_db()
        return Response(
            {
                'ok': True,
                'proration_behavior': proration_behavior,
                'subscription_id': tenant.stripe_subscription_id,
                'subscription_status': tenant.subscription_status,
                'plan_name': tenant.plan_name,
                'plan_interval': tenant.plan_interval,
                'device_limit': tenant.device_limit,
            }
        )
    except ValidationError as e:
        return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception('change subscription: %s', e)
        return Response({'detail': str(e)[:500]}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_billing_portal_session(request):
    """POST /api/platform/billing/portal-session/ — Stripe Customer Portal."""
    if not _saas_enabled():
        return Response({'detail': 'SaaS billing is not enabled.'}, status=status.HTTP_403_FORBIDDEN)
    if not (RolePermissions.can_manage_all(request.user) or request.user.is_manager()):
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        tenant = _resolve_request_tenant(request.user)
    except Exception as e:
        logger.exception('portal tenant bootstrap: %s', e)
        return Response({'detail': 'Could not provision tenant for this account.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not tenant or not tenant.stripe_customer_id:
        return Response({'detail': 'No Stripe customer for this tenant.'}, status=status.HTTP_400_BAD_REQUEST)
    secret = get_stripe_secret_key()
    if not secret:
        return Response({'detail': 'Stripe is not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    cfg = get_stripe_billing_config()
    if not cfg.customer_portal_enabled:
        return Response(
            {'detail': 'Stripe customer portal is disabled in platform settings.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    try:
        import stripe
    except ImportError:
        return Response({'detail': 'stripe package not installed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    stripe.api_key = secret
    base = billing_redirect_base()
    try:
        return_url = validate_billing_redirect_url(
            request.data.get('return_url') or f'{base}/settings',
            field_name='return_url',
        )
    except ValueError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    try:
        portal = stripe.billing_portal.Session.create(
            customer=tenant.stripe_customer_id,
            return_url=return_url,
        )
        return Response({'url': portal.url})
    except Exception as e:
        logger.exception('portal session: %s', e)
        return Response({'detail': str(e)[:500]}, status=status.HTTP_502_BAD_GATEWAY)
