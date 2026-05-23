"""Serializers for subscription catalog and billing settings."""

from __future__ import annotations

from rest_framework import serializers

from .pricing_models import BillingPromotion, PlatformBillingSettings, StripeBillingConfig, SubscriptionPlan


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

    def validate(self, attrs):
        attrs = super().validate(attrs)
        kind = attrs.get('kind', getattr(self.instance, 'kind', SubscriptionPlan.KIND_FREE))
        stripe_price_id = attrs.get('stripe_price_id', getattr(self.instance, 'stripe_price_id', ''))
        stripe_price_id = (stripe_price_id or '').strip()
        included_screens = attrs.get('included_screens', getattr(self.instance, 'included_screens', None))
        min_quantity = attrs.get('min_quantity', getattr(self.instance, 'min_quantity', 1))
        is_unlimited = attrs.get('is_unlimited', getattr(self.instance, 'is_unlimited', False))

        if kind != SubscriptionPlan.KIND_FREE:
            if not stripe_price_id:
                raise serializers.ValidationError(
                    {'stripe_price_id': 'Paid plans require a Stripe Price ID (price_...).'}
                )
            if not stripe_price_id.startswith('price_'):
                raise serializers.ValidationError(
                    {'stripe_price_id': 'Stripe Price ID must start with "price_".'}
                )
        if kind == SubscriptionPlan.KIND_BUNDLE and not included_screens:
            raise serializers.ValidationError(
                {'included_screens': 'Bundle plans require included_screens (for example: 5).'}
            )
        if kind == SubscriptionPlan.KIND_PER_SCREEN and int(min_quantity or 0) < 1:
            raise serializers.ValidationError(
                {'min_quantity': 'Per-screen plans require min_quantity >= 1.'}
            )
        if kind == SubscriptionPlan.KIND_VIP and not bool(is_unlimited):
            raise serializers.ValidationError(
                {'is_unlimited': 'VIP plans must be marked unlimited.'}
            )

        return attrs


class PlatformBillingSettingsSerializer(serializers.ModelSerializer):
    stripe_publishable_key = serializers.CharField(required=False, allow_blank=True)
    stripe_secret_key = serializers.CharField(required=False, allow_blank=True, write_only=True)
    stripe_webhook_secret = serializers.CharField(required=False, allow_blank=True, write_only=True)
    stripe_secret_key_configured = serializers.SerializerMethodField()
    stripe_webhook_secret_configured = serializers.SerializerMethodField()
    stripe_publishable_key_configured = serializers.SerializerMethodField()
    stripe_secret_key_masked = serializers.SerializerMethodField()
    stripe_webhook_secret_masked = serializers.SerializerMethodField()
    stripe_default_currency = serializers.CharField(required=False, allow_blank=True)
    stripe_customer_portal_enabled = serializers.BooleanField(required=False)

    class Meta:
        model = PlatformBillingSettings
        fields = [
            'default_free_screen_limit',
            'trial_days_display',
            'checkout_allow_promotion_codes',
            'stripe_publishable_key',
            'stripe_publishable_key_configured',
            'stripe_secret_key',
            'stripe_secret_key_masked',
            'stripe_secret_key_configured',
            'stripe_webhook_secret',
            'stripe_webhook_secret_masked',
            'stripe_webhook_secret_configured',
            'stripe_default_currency',
            'stripe_customer_portal_enabled',
        ]

    def _stripe_config(self) -> StripeBillingConfig:
        return StripeBillingConfig.get_solo()

    def _mask(self, value: str) -> str:
        s = (value or '').strip()
        if not s:
            return ''
        if len(s) <= 8:
            return '*' * len(s)
        return f'{s[:4]}{"*" * (len(s) - 8)}{s[-4:]}'

    def get_stripe_secret_key_configured(self, _obj) -> bool:
        return bool(self._stripe_config().secret_key_encrypted)

    def get_stripe_webhook_secret_configured(self, _obj) -> bool:
        return bool(self._stripe_config().webhook_secret_encrypted)

    def get_stripe_publishable_key_configured(self, _obj) -> bool:
        return bool((self._stripe_config().publishable_key or '').strip())

    def get_stripe_secret_key_masked(self, _obj) -> str:
        key = self._stripe_config().get_secret_key()
        return self._mask(key)

    def get_stripe_webhook_secret_masked(self, _obj) -> str:
        key = self._stripe_config().get_webhook_secret()
        return self._mask(key)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        cfg = self._stripe_config()
        data['stripe_publishable_key'] = (cfg.publishable_key or '').strip()
        data['stripe_default_currency'] = (cfg.default_currency or 'usd').lower()
        data['stripe_customer_portal_enabled'] = bool(cfg.customer_portal_enabled)
        return data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        pk = (attrs.get('stripe_publishable_key') or '').strip()
        sk = (attrs.get('stripe_secret_key') or '').strip()
        wh = (attrs.get('stripe_webhook_secret') or '').strip()
        cur = (attrs.get('stripe_default_currency') or '').strip().lower()

        if pk and not (pk.startswith('pk_live_') or pk.startswith('pk_test_')):
            raise serializers.ValidationError(
                {'stripe_publishable_key': 'Stripe publishable key must start with pk_live_ or pk_test_.'}
            )
        if sk and not (
            sk.startswith('sk_live_')
            or sk.startswith('sk_test_')
            or sk.startswith('rk_live_')
            or sk.startswith('rk_test_')
        ):
            raise serializers.ValidationError(
                {
                    'stripe_secret_key': (
                        'Stripe secret key must start with sk_live_, sk_test_, rk_live_, or rk_test_.'
                    )
                }
            )
        if wh and not wh.startswith('whsec_'):
            raise serializers.ValidationError(
                {'stripe_webhook_secret': 'Stripe webhook secret must start with whsec_.'}
            )
        if cur and len(cur) > 8:
            raise serializers.ValidationError({'stripe_default_currency': 'Currency is too long.'})
        return attrs

    def update(self, instance, validated_data):
        cfg = self._stripe_config()
        publishable = validated_data.pop('stripe_publishable_key', None)
        secret = validated_data.pop('stripe_secret_key', None)
        webhook = validated_data.pop('stripe_webhook_secret', None)
        currency = validated_data.pop('stripe_default_currency', None)
        portal_enabled = validated_data.pop('stripe_customer_portal_enabled', None)

        instance = super().update(instance, validated_data)

        if publishable is not None:
            cfg.publishable_key = (publishable or '').strip()
        if secret is not None:
            secret = (secret or '').strip()
            if secret:
                cfg.set_secret_key(secret)
            else:
                cfg.clear_secret_key()
        if webhook is not None:
            webhook = (webhook or '').strip()
            if webhook:
                cfg.set_webhook_secret(webhook)
            else:
                cfg.clear_webhook_secret()
        if currency is not None:
            cfg.default_currency = (currency or 'usd').strip().lower() or 'usd'
        if portal_enabled is not None:
            cfg.customer_portal_enabled = bool(portal_enabled)
        cfg.save()
        return instance


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
