from django.db import migrations


def backfill_local_trials(apps, schema_editor):
    Tenant = apps.get_model('saas_platform', 'Tenant')
    PlatformBillingSettings = apps.get_model('saas_platform', 'PlatformBillingSettings')
    UserSubscription = apps.get_model('accounts', 'UserSubscription')
    User = apps.get_model('accounts', 'User')

    from datetime import timedelta
    from django.utils import timezone

    solo = PlatformBillingSettings.objects.filter(pk=1).first()
    days = int(getattr(solo, 'trial_days_display', None) or 14)

    tenants = Tenant.objects.filter(
        trial_end__isnull=True,
        stripe_subscription_id='',
    ).exclude(subscription_status__in=('active', 'past_due', 'canceled', 'unpaid', 'paused'))

    for tenant in tenants.iterator():
        anchor = tenant.created_at or timezone.now()
        tenant.trial_end = anchor + timedelta(days=days)
        tenant.subscription_status = 'trialing'
        tenant.save(update_fields=['trial_end', 'subscription_status', 'updated_at'])

        for user in User.objects.filter(tenant_id=tenant.pk).iterator():
            UserSubscription.objects.update_or_create(
                user_id=user.id,
                defaults={
                    'plan_key': '',
                    'plan_name': tenant.plan_name or '',
                    'plan_interval': tenant.plan_interval or '',
                    'status': tenant.subscription_status or 'trialing',
                    'trial_end': tenant.trial_end,
                    'current_period_start': tenant.current_period_start,
                    'current_period_end': tenant.current_period_end,
                    'cancel_at_period_end': bool(tenant.cancel_at_period_end),
                    'provider_customer_id': tenant.stripe_customer_id or '',
                    'provider_subscription_id': tenant.stripe_subscription_id or '',
                    'device_limit': tenant.device_limit,
                    'metadata': {'source': 'local_trial_backfill'},
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ('saas_platform', '0009_stripe_billing_config'),
        ('accounts', '0009_backfill_user_subscriptions'),
    ]

    operations = [
        migrations.RunPython(backfill_local_trials, migrations.RunPython.noop),
    ]
