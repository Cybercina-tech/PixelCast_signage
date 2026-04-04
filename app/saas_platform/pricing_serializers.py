"""Serializers for subscription catalog and billing settings."""

from __future__ import annotations

from rest_framework import serializers

from .pricing_models import BillingPromotion, PlatformBillingSettings, SubscriptionPlan


class PublicSubscriptionPlanSerializer(serializers.ModelSerializer):
    checkout_available = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            'key',
            'label',
            'description',
            'kind',
            'included_screens',
            'is_unlimited',
            'min_quantity',
            'display_amount_cents',
            'currency',
            'sort_order',
            'badge',
            'highlight',
            'checkout_available',
        ]

    def get_checkout_available(self, obj):
        if obj.kind == SubscriptionPlan.KIND_FREE:
            return True
        return bool((obj.stripe_price_id or '').strip())


class SubscriptionPlanWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'key',
            'label',
            'description',
            'kind',
            'included_screens',
            'is_unlimited',
            'stripe_price_id',
            'min_quantity',
            'display_amount_cents',
            'currency',
            'sort_order',
            'is_active',
            'badge',
            'highlight',
        ]


class PlatformBillingSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformBillingSettings
        fields = [
            'default_free_screen_limit',
            'trial_days_display',
            'checkout_allow_promotion_codes',
        ]


class BillingPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingPromotion
        fields = [
            'id',
            'label',
            'stripe_promotion_code_id',
            'is_active',
            'sort_order',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
