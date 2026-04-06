from __future__ import annotations

import uuid

from django.db import models


class InstanceRegistry(models.Model):
    """One row per registered self-hosted instance (CodeCanyon purchase + domain)."""

    STATUS_ACTIVE = "active"
    STATUS_SUSPENDED = "suspended"
    STATUS_EXPIRED = "expired"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_SUSPENDED, "Suspended"),
        (STATUS_EXPIRED, "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_code_fingerprint = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="SHA-256 hex of normalized purchase code (never store raw code).",
    )
    domain = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    api_key_hash = models.CharField(max_length=64, unique=True, db_index=True)
    version = models.CharField(max_length=20, blank=True, default="")
    license_status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True,
    )
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "platform_gateway_instance_registry"
        ordering = ["-last_heartbeat_at", "-first_seen_at"]

    def __str__(self):
        return f"GatewayInstance({self.domain})"


class InstanceUsageLog(models.Model):
    """Time-series usage reported by an instance."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(
        InstanceRegistry,
        on_delete=models.CASCADE,
        related_name="usage_logs",
    )
    reported_at = models.DateTimeField(db_index=True)
    active_screens = models.IntegerField(default=0)
    templates_count = models.IntegerField(default=0)
    storage_used_mb = models.FloatField(default=0)
    commands_sent = models.IntegerField(default=0)
    users_count = models.IntegerField(default=0)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "platform_gateway_instance_usage_log"
        ordering = ["-reported_at"]
        indexes = [
            models.Index(fields=["instance", "reported_at"]),
        ]


class InstanceHeartbeat(models.Model):
    """Per-heartbeat audit row."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(
        InstanceRegistry,
        on_delete=models.CASCADE,
        related_name="heartbeat_logs",
    )
    received_at = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=20, blank=True, default="")
    status = models.CharField(max_length=50, default="ok")
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "platform_gateway_instance_heartbeat"
        ordering = ["-received_at"]
        indexes = [
            models.Index(fields=["instance", "received_at"]),
        ]


class GatewayRegistrationAttempt(models.Model):
    """Audit trail for register-instance (no raw purchase codes)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    purchase_code_fingerprint = models.CharField(max_length=64, db_index=True)
    outcome = models.CharField(max_length=32, db_index=True)
    http_status = models.PositiveSmallIntegerField(default=0)
    detail = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "platform_gateway_registration_attempt"
        ordering = ["-created_at"]
