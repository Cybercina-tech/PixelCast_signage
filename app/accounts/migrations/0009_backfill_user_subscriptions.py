from django.db import migrations


def backfill_user_subscriptions(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    UserSubscription = apps.get_model('accounts', 'UserSubscription')

    for user in User.objects.select_related('tenant').all().iterator():
        tenant = getattr(user, 'tenant', None)
        if not tenant:
            continue
        UserSubscription.objects.update_or_create(
            user_id=user.id,
            defaults={
                'plan_key': '',
                'plan_name': getattr(tenant, 'plan_name', '') or '',
                'plan_interval': getattr(tenant, 'plan_interval', '') or '',
                'status': getattr(tenant, 'subscription_status', 'none') or 'none',
                'trial_end': getattr(tenant, 'trial_end', None),
                'current_period_start': getattr(tenant, 'current_period_start', None),
                'current_period_end': getattr(tenant, 'current_period_end', None),
                'cancel_at_period_end': bool(getattr(tenant, 'cancel_at_period_end', False)),
                'provider_customer_id': getattr(tenant, 'stripe_customer_id', '') or '',
                'provider_subscription_id': getattr(tenant, 'stripe_subscription_id', '') or '',
                'device_limit': getattr(tenant, 'device_limit', None),
                'metadata': {'source': 'tenant_backfill'},
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0008_usersubscription'),
    ]

    operations = [
        migrations.RunPython(backfill_user_subscriptions, migrations.RunPython.noop),
    ]
