from django.contrib import admin

from .models import (
    GatewayRegistrationAttempt,
    InstanceHeartbeat,
    InstanceRegistry,
    InstanceUsageLog,
)


@admin.register(InstanceRegistry)
class InstanceRegistryAdmin(admin.ModelAdmin):
    list_display = ("id", "domain", "license_status", "is_online", "last_heartbeat_at", "version")
    list_filter = ("license_status", "is_online")
    search_fields = ("domain", "purchase_code_fingerprint")
    readonly_fields = ("id", "first_seen_at", "purchase_code_fingerprint", "api_key_hash")


@admin.register(InstanceUsageLog)
class InstanceUsageLogAdmin(admin.ModelAdmin):
    list_display = ("instance", "reported_at", "active_screens", "users_count")
    list_select_related = ("instance",)


@admin.register(InstanceHeartbeat)
class InstanceHeartbeatAdmin(admin.ModelAdmin):
    list_display = ("instance", "received_at", "version", "status", "ip_address")
    list_select_related = ("instance",)


@admin.register(GatewayRegistrationAttempt)
class GatewayRegistrationAttemptAdmin(admin.ModelAdmin):
    list_display = ("created_at", "outcome", "http_status", "ip_address", "purchase_code_fingerprint")
    list_filter = ("outcome",)
