"""Public pricing list and platform-admin catalog CRUD."""

from __future__ import annotations

import logging

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .permissions import IsDeveloper
from .pricing_models import BillingPromotion, PlatformBillingSettings, StripeBillingConfig, SubscriptionPlan
from .pricing_serializers import (
    BillingPromotionSerializer,
    PlatformBillingSettingsSerializer,
    PublicSubscriptionPlanSerializer,
    SubscriptionPlanWriteSerializer,
)
from .stripe_config import get_stripe_publishable_key, get_stripe_secret_key, get_stripe_webhook_secret
from .views import PlatformSaaSViewSet

logger = logging.getLogger(__name__)


def _stripe_env_status() -> dict:
    """Non-secret Stripe readiness flags for platform operators."""
    cfg = StripeBillingConfig.get_solo()
    secret = bool(get_stripe_secret_key())
    webhook = bool(get_stripe_webhook_secret())
    publishable = bool(get_stripe_publishable_key())
    legacy_price = bool((getattr(settings, 'STRIPE_PRICE_ID', '') or '').strip())
    active_paid_plans = SubscriptionPlan.objects.filter(
        is_active=True,
    ).exclude(kind=SubscriptionPlan.KIND_FREE).exclude(stripe_price_id='').count()
    return {
        'config_source': 'database',
        'has_env_fallback': bool(
            (getattr(settings, 'STRIPE_SECRET_KEY', '') or '').strip()
            or (getattr(settings, 'STRIPE_WEBHOOK_SECRET', '') or '').strip()
            or (getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '') or '').strip()
        ),
        'stripe_secret_key_configured': secret,
        'stripe_webhook_secret_configured': webhook,
        'stripe_publishable_key_configured': publishable,
        'stripe_legacy_price_id_configured': legacy_price,
        'default_currency': (cfg.default_currency or 'usd').lower(),
        'customer_portal_enabled': bool(cfg.customer_portal_enabled),
        'checkout_ready': secret and (active_paid_plans > 0 or legacy_price),
        'webhook_ready': secret and webhook,
        'active_paid_plans_with_price': active_paid_plans,
        'public_web_app_url': (getattr(settings, 'PUBLIC_WEB_APP_URL', '') or '').strip(),
        'stripe_grace_period_days': int(getattr(settings, 'STRIPE_GRACE_PERIOD_DAYS', 7) or 7),
    }


def _saas_enabled():
    return bool(getattr(settings, 'PLATFORM_SAAS_ENABLED', False))


@api_view(['GET'])
@permission_classes([AllowAny])
def public_pricing(request):
    """GET /api/public/pricing/ — active plans + defaults (no secrets)."""
    solo = PlatformBillingSettings.get_solo()
    plans = (
        SubscriptionPlan.objects.filter(is_active=True)
        .order_by('sort_order', 'key')
    )
    return Response(
        {
            'plans': PublicSubscriptionPlanSerializer(plans, many=True).data,
            'default_free_screen_limit': solo.default_free_screen_limit,
            'trial_days_display': solo.trial_days_display,
            'saas_enabled': _saas_enabled(),
        }
    )


class SubscriptionPlanViewSet(PlatformSaaSViewSet):
    """Developer CRUD for SubscriptionPlan."""

    queryset = SubscriptionPlan.objects.all().order_by('sort_order', 'key')
    serializer_class = SubscriptionPlanWriteSerializer
    lookup_field = 'key'


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_stripe_status(request):
    """GET /api/platform/pricing/stripe-status/ — env readiness (no secret values)."""
    if not _saas_enabled():
        return Response(
            {'detail': 'Platform SaaS features are disabled (set PLATFORM_SAAS_ENABLED=true).'},
            status=status.HTTP_403_FORBIDDEN,
        )
    return Response(_stripe_env_status())


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_billing_settings(request):
    """GET/PATCH /api/platform/pricing/settings/ — singleton billing defaults."""
    if not _saas_enabled():
        return Response(
            {'detail': 'Platform SaaS features are disabled (set PLATFORM_SAAS_ENABLED=true).'},
            status=status.HTTP_403_FORBIDDEN,
        )
    solo = PlatformBillingSettings.get_solo()
    if request.method == 'GET':
        return Response(PlatformBillingSettingsSerializer(solo).data)
    ser = PlatformBillingSettingsSerializer(solo, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)


class BillingPromotionViewSet(PlatformSaaSViewSet):
    queryset = BillingPromotion.objects.all().order_by('sort_order', 'label')
    serializer_class = BillingPromotionSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_stripe_connection_health(request):
    """GET /api/platform/pricing/stripe-connection-health/ — API reachability diagnostics."""
    if not _saas_enabled():
        return Response(
            {'detail': 'Platform SaaS features are disabled (set PLATFORM_SAAS_ENABLED=true).'},
            status=status.HTTP_403_FORBIDDEN,
        )
    cfg = StripeBillingConfig.get_solo()
    secret = get_stripe_secret_key()
    publishable = get_stripe_publishable_key()
    webhook = get_stripe_webhook_secret()
    paid_plans = list(
        SubscriptionPlan.objects.filter(is_active=True)
        .exclude(kind=SubscriptionPlan.KIND_FREE)
        .values('key', 'label', 'stripe_price_id')
        .order_by('sort_order', 'key')
    )
    missing_price_plan_keys = [
        row['key']
        for row in paid_plans
        if not (row.get('stripe_price_id') or '').strip().startswith('price_')
    ]
    checks = {
        'stripe_secret_key_configured': bool(secret),
        'stripe_publishable_key_configured': bool(publishable),
        'stripe_webhook_secret_configured': bool(webhook),
        'paid_plan_price_coverage': len(missing_price_plan_keys) == 0 and len(paid_plans) > 0,
    }
    blocking_reasons: list[str] = []
    if not checks['stripe_secret_key_configured']:
        blocking_reasons.append('Stripe secret key is missing.')
    if not checks['stripe_publishable_key_configured']:
        blocking_reasons.append('Stripe publishable key is missing.')
    if not checks['stripe_webhook_secret_configured']:
        blocking_reasons.append('Stripe webhook signing secret is missing.')
    if not paid_plans:
        blocking_reasons.append('No active paid plans found.')
    elif missing_price_plan_keys:
        blocking_reasons.append(
            f'Active paid plans without valid Stripe price id: {", ".join(missing_price_plan_keys)}.'
        )

    diag = {
        'api_reachable': False,
        'mode': '',
        'account_id': '',
        'charges_enabled': False,
        'details_submitted': False,
        'message': '',
        'stripe_secret_key_configured': checks['stripe_secret_key_configured'],
        'stripe_publishable_key_configured': checks['stripe_publishable_key_configured'],
        'stripe_webhook_secret_configured': checks['stripe_webhook_secret_configured'],
        'ready': False,
        'checks': checks,
        'blocking_reasons': blocking_reasons,
        'active_paid_plan_keys': [row['key'] for row in paid_plans],
        'missing_price_plan_keys': missing_price_plan_keys,
    }
    if not secret:
        diag['message'] = 'Stripe secret key is not configured.'
        diag['ready'] = False
        return Response(diag)
    try:
        import stripe

        stripe.api_key = secret
        account = stripe.Account.retrieve()
        diag['api_reachable'] = True
        diag['mode'] = 'live' if secret.startswith('sk_live_') else 'test'
        diag['account_id'] = str(getattr(account, 'id', '') or account.get('id', ''))
        diag['charges_enabled'] = bool(
            getattr(account, 'charges_enabled', None)
            if not isinstance(account, dict)
            else account.get('charges_enabled')
        )
        diag['details_submitted'] = bool(
            getattr(account, 'details_submitted', None)
            if not isinstance(account, dict)
            else account.get('details_submitted')
        )
        diag['message'] = 'Stripe API connection is healthy.'
        if not diag['charges_enabled']:
            blocking_reasons.append('Stripe account charges are not enabled.')
        if not diag['details_submitted']:
            blocking_reasons.append('Stripe account onboarding details are incomplete.')
        diag['ready'] = diag['api_reachable'] and len(blocking_reasons) == 0
    except Exception as e:
        logger.warning('Stripe health check failed: %s', e)
        diag['message'] = str(e)[:500]
        diag['ready'] = False
        if 'Stripe API is not reachable.' not in blocking_reasons:
            blocking_reasons.append('Stripe API is not reachable.')
    return Response(diag)
