from django.contrib import admin

from .models import (
    BillingWebhookEvent,
    Tenant,
    TenantApiKey,
    TenantAuditLog,
    TenantInvoice,
    TenantWebhookEndpoint,
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'subscription_status',
        'stripe_customer_id',
        'plan_name',
        'device_limit',
        'updated_at',
    )
    search_fields = ('name', 'slug', 'stripe_customer_id', 'organization_name_key')
    list_filter = ('subscription_status',)


@admin.register(TenantInvoice)
class TenantInvoiceAdmin(admin.ModelAdmin):
    list_display = ('stripe_invoice_id', 'tenant', 'status', 'amount_due', 'currency', 'created_at')
    search_fields = ('stripe_invoice_id', 'number')


@admin.register(BillingWebhookEvent)
class BillingWebhookEventAdmin(admin.ModelAdmin):
    list_display = ('stripe_event_id', 'event_type', 'tenant', 'processed_ok', 'created_at')
    list_filter = ('event_type', 'processed_ok')


@admin.register(TenantApiKey)
class TenantApiKeyAdmin(admin.ModelAdmin):
    list_display = ('label', 'tenant', 'prefix', 'created_at', 'revoked_at')
    search_fields = ('label', 'prefix')


@admin.register(TenantWebhookEndpoint)
class TenantWebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'url', 'is_active', 'created_at')


@admin.register(TenantAuditLog)
class TenantAuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'tenant', 'actor', 'created_at')
    list_filter = ('action',)
