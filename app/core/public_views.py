"""Public (unauthenticated) JSON endpoints for SPA / clients."""

from __future__ import annotations

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.deployment import deployment_public_payload
from saas_platform.stripe_config import get_stripe_publishable_key


@require_GET
def public_deployment(request):
    """
    Deployment flags for routing and feature toggles (no secrets).
    """
    from core.deployment import resolve_effective_platform_saas

    effective_saas = resolve_effective_platform_saas(
        getattr(settings, 'DEPLOYMENT_MODE', 'hybrid'),
        getattr(settings, 'PLATFORM_SAAS_ENABLED', False),
    )
    payload = deployment_public_payload(
        getattr(settings, 'DEPLOYMENT_MODE', 'hybrid'),
        effective_saas,
        get_stripe_publishable_key(),
        getattr(settings, 'PLATFORM_GATEWAY_ENABLED', False),
    )
    return JsonResponse(payload)
