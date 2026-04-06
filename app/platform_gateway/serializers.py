from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers


class RegisterInstanceSerializer(serializers.Serializer):
    purchase_code = serializers.CharField(max_length=255)
    domain = serializers.CharField(max_length=255)
    version = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")


class HeartbeatSerializer(serializers.Serializer):
    version = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    status = serializers.CharField(max_length=50, required=False, allow_blank=True, default="ok")


class UsageReportSerializer(serializers.Serializer):
    active_screens = serializers.IntegerField(min_value=0, default=0)
    templates_count = serializers.IntegerField(min_value=0, default=0)
    storage_used_mb = serializers.FloatField(min_value=0, default=0)
    commands_sent = serializers.IntegerField(min_value=0, default=0)
    users_count = serializers.IntegerField(min_value=0, default=0)
    reported_at = serializers.DateTimeField()

    def validate_reported_at(self, value):
        now = timezone.now()
        if value > now + timedelta(minutes=5):
            raise serializers.ValidationError("reported_at cannot be more than 5 minutes in the future")
        if value < now - timedelta(hours=24):
            raise serializers.ValidationError("reported_at cannot be older than 24 hours")
        return value


class GatewayTicketSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    body = serializers.CharField()
    priority = serializers.ChoiceField(
        choices=["low", "medium", "high", "critical"],
        default="medium",
    )
    customer_email = serializers.EmailField(required=False, allow_blank=True, default="")
    remote_ticket_id = serializers.UUIDField(required=False, allow_null=True)
    attachments = serializers.ListField(child=serializers.JSONField(), required=False, default=list)
