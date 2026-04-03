"""
Deployment mode matrix (SaaS vs self-hosted vs hybrid).

Use resolve_effective_platform_saas() from settings; do not duplicate logic in views.
"""

from __future__ import annotations

from typing import Any, Literal

DeploymentMode = Literal['saas', 'self_hosted', 'hybrid']

VALID_MODES = frozenset({'saas', 'self_hosted', 'hybrid'})


def normalize_deployment_mode(raw: str | None) -> DeploymentMode:
    """Return a valid deployment mode; invalid values fall back to hybrid."""
    if not raw:
        return 'hybrid'
    v = str(raw).strip().lower()
    if v in VALID_MODES:
        return v  # type: ignore[return-value]
    return 'hybrid'


def resolve_effective_platform_saas(deployment_mode: str | None, platform_saas_env_flag: bool) -> bool:
    """
    Effective PLATFORM_SAAS_ENABLED after applying DEPLOYMENT_MODE.

    - self_hosted: SaaS platform features are always off (Stripe webhooks, tenant admin UI, etc.).
    - saas: always on (operator runs a SaaS deployment).
    - hybrid: follows PLATFORM_SAAS_ENABLED env (buyer can enable SaaS or stay license-only).
    """
    mode = normalize_deployment_mode(deployment_mode)
    if mode == 'self_hosted':
        return False
    if mode == 'saas':
        return True
    return bool(platform_saas_env_flag)


def deployment_public_payload(
    deployment_mode: str | None,
    effective_platform_saas: bool,
    stripe_publishable_key: str = '',
) -> dict[str, Any]:
    """Safe JSON for anonymous clients (SPA routing / feature toggles)."""
    mode = normalize_deployment_mode(deployment_mode)
    return {
        'deployment_mode': mode,
        'platform_saas_enabled': bool(effective_platform_saas),
        'stripe_publishable_key_configured': bool((stripe_publishable_key or '').strip()),
    }
