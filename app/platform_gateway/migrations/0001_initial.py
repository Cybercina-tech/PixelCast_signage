# Generated manually for platform_gateway

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="InstanceRegistry",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("purchase_code_fingerprint", models.CharField(db_index=True, help_text="SHA-256 hex of normalized purchase code (never store raw code).", max_length=64, unique=True)),
                ("domain", models.CharField(db_index=True, max_length=255)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("api_key_hash", models.CharField(db_index=True, max_length=64, unique=True)),
                ("version", models.CharField(blank=True, default="", max_length=20)),
                ("license_status", models.CharField(choices=[("active", "Active"), ("suspended", "Suspended"), ("expired", "Expired")], db_index=True, default="active", max_length=16)),
                ("first_seen_at", models.DateTimeField(auto_now_add=True)),
                ("last_heartbeat_at", models.DateTimeField(blank=True, null=True)),
                ("is_online", models.BooleanField(default=False)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "platform_gateway_instance_registry",
                "ordering": ["-last_heartbeat_at", "-first_seen_at"],
            },
        ),
        migrations.CreateModel(
            name="InstanceUsageLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reported_at", models.DateTimeField(db_index=True)),
                ("active_screens", models.IntegerField(default=0)),
                ("templates_count", models.IntegerField(default=0)),
                ("storage_used_mb", models.FloatField(default=0)),
                ("commands_sent", models.IntegerField(default=0)),
                ("users_count", models.IntegerField(default=0)),
                ("extra_data", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("instance", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="usage_logs", to="platform_gateway.instanceregistry")),
            ],
            options={
                "db_table": "platform_gateway_instance_usage_log",
                "ordering": ["-reported_at"],
            },
        ),
        migrations.CreateModel(
            name="InstanceHeartbeat",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("version", models.CharField(blank=True, default="", max_length=20)),
                ("status", models.CharField(default="ok", max_length=50)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("instance", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="heartbeat_logs", to="platform_gateway.instanceregistry")),
            ],
            options={
                "db_table": "platform_gateway_instance_heartbeat",
                "ordering": ["-received_at"],
            },
        ),
        migrations.CreateModel(
            name="GatewayRegistrationAttempt",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("purchase_code_fingerprint", models.CharField(db_index=True, max_length=64)),
                ("outcome", models.CharField(db_index=True, max_length=32)),
                ("http_status", models.PositiveSmallIntegerField(default=0)),
                ("detail", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "platform_gateway_registration_attempt",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="instanceusagelog",
            index=models.Index(fields=["instance", "reported_at"], name="platform_ga_instanc_2b5f8e_idx"),
        ),
        migrations.AddIndex(
            model_name="instanceheartbeat",
            index=models.Index(fields=["instance", "received_at"], name="platform_ga_instanc_8a1c2d_idx"),
        ),
    ]
