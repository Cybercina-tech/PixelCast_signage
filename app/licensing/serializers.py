from rest_framework import serializers


class LicenseStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
    license_status = serializers.CharField()
    grace_until = serializers.DateTimeField(allow_null=True)
    activated_domain = serializers.CharField(allow_blank=True)
    product_id = serializers.CharField(allow_blank=True)
    product_id_source = serializers.CharField()
    last_validation_at = serializers.DateTimeField(allow_null=True)
    last_successful_validation_at = serializers.DateTimeField(allow_null=True)
    enforcement_enabled = serializers.BooleanField()


class LicenseActivateSerializer(serializers.Serializer):
    purchase_code = serializers.CharField(max_length=128)
    domain = serializers.CharField(max_length=255, required=False, allow_blank=True)
    codecanyon_product_id_override = serializers.CharField(
        max_length=64, required=False, allow_blank=True
    )


class LicenseRevalidateSerializer(serializers.Serializer):
    force = serializers.BooleanField(required=False, default=True)
