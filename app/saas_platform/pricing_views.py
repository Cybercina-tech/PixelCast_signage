"""Public pricing list and platform-admin catalog CRUD."""

from __future__ import annotations

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .permissions import IsDeveloper
from .pricing_models import BillingPromotion, PlatformBillingSettings, SubscriptionPlan
from .pricing_serializers import (
    BillingPromotionSerializer,
    PlatformBillingSettingsSerializer,
    PublicSubscriptionPlanSerializer,
    SubscriptionPlanWriteSerializer,
)
from .views import PlatformSaaSViewSet


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
