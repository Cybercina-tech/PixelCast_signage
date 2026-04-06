# platform_gateway bridged tickets

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("platform_gateway", "0001_initial"),
        ("tickets", "0005_ensure_ticket_telemetry_columns"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="source",
            field=models.CharField(
                choices=[
                    ("web", "Web"),
                    ("email", "Email"),
                    ("api", "API"),
                    ("chat", "Chat"),
                    ("gateway_cc", "CodeCanyon gateway"),
                ],
                default="web",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="gateway_instance",
            field=models.ForeignKey(
                blank=True,
                help_text="Operator platform_gateway row when ingested via CodeCanyon gateway API",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tickets",
                to="platform_gateway.instanceregistry",
            ),
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.UniqueConstraint(
                condition=Q(gateway_instance__isnull=False, remote_ticket_id__isnull=False),
                fields=("gateway_instance", "remote_ticket_id"),
                name="tickets_ticket_gateway_instance_remote_uid",
            ),
        ),
    ]
