"""Resolve Stripe Checkout line items and subscription metadata from SubscriptionPlan."""

from __future__ import annotations

from dataclasses import dataclass

from rest_framework.exceptions import ValidationError

from .pricing_models import SubscriptionPlan


@dataclass
class CheckoutResolution:
    line_items: list[dict]
    device_limit_meta: str  # digits or "unlimited"
    plan_key: str


def resolve_checkout_for_plan(
    plan: SubscriptionPlan,
    quantity: int | None,
) -> CheckoutResolution:
    """Build Stripe line_items and device_limit string for subscription metadata."""
    if plan.kind == SubscriptionPlan.KIND_FREE:
        raise ValidationError('Free plan does not use Stripe checkout.')

    price = (plan.stripe_price_id or '').strip()
    if not price:
        raise ValidationError('This plan has no Stripe price configured.')

    if plan.kind == SubscriptionPlan.KIND_VIP:
        if not plan.is_unlimited:
            raise ValidationError('VIP plan must be marked unlimited.')
        return CheckoutResolution(
            line_items=[{'price': price, 'quantity': 1}],
            device_limit_meta='unlimited',
            plan_key=plan.key,
        )

    if plan.kind == SubscriptionPlan.KIND_BUNDLE:
        if not plan.included_screens:
            raise ValidationError('Bundle plan needs included_screens.')
        return CheckoutResolution(
            line_items=[{'price': price, 'quantity': 1}],
            device_limit_meta=str(int(plan.included_screens)),
            plan_key=plan.key,
        )

    if plan.kind == SubscriptionPlan.KIND_PER_SCREEN:
        q = int(quantity or plan.min_quantity)
        q = max(q, int(plan.min_quantity))
        return CheckoutResolution(
            line_items=[{'price': price, 'quantity': q}],
            device_limit_meta=str(q),
            plan_key=plan.key,
        )

    raise ValidationError('Unsupported plan kind.')
