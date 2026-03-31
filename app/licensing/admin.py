from django.contrib import admin
from .models import LicenseState


@admin.register(LicenseState)
class LicenseStateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "license_status",
        "activated_domain",
        "masked_code",
        "last_successful_validation_at",
        "grace_until",
        "updated_at",
    )
    readonly_fields = (
        "validation_signature",
        "last_validation_at",
        "last_successful_validation_at",
        "created_at",
        "updated_at",
    )
    fields = (
        "purchase_code",
        "activated_domain",
        "activated_at",
        "license_status",
        "codecanyon_product_id_override",
        "last_validation_at",
        "last_successful_validation_at",
        "grace_until",
        "last_error",
        "validation_signature",
        "created_at",
        "updated_at",
    )

    def masked_code(self, obj):
        return obj.masked_purchase_code()

    masked_code.short_description = "Purchase code"
