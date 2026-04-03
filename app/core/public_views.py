"""Public (unauthenticated) JSON endpoints for SPA / clients."""

from __future__ import annotations

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.deployment import deployment_public_payload


@require_GET
def public_deployment(request):
    """
    Deployment flags for routing and feature toggles (no secrets).
    """
    payload = deployment_public_payload(
        getattr(settings, 'DEPLOYMENT_MODE', 'hybrid'),
        getattr(settings, 'PLATFORM_SAAS_ENABLED', False),
        getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '') or '',
    )
    return JsonResponse(payload)
