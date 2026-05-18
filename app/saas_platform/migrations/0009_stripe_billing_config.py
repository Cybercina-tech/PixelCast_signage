from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saas_platform', '0008_ensure_user_tenants'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeBillingConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publishable_key', models.CharField(blank=True, default='', help_text='Stripe publishable key (pk_live_... / pk_test_...).', max_length=255)),
                ('secret_key_encrypted', models.TextField(blank=True, default='', help_text='Encrypted Stripe secret key.')),
                ('webhook_secret_encrypted', models.TextField(blank=True, default='', help_text='Encrypted Stripe webhook signing secret.')),
                ('default_currency', models.CharField(default='usd', max_length=8)),
                ('customer_portal_enabled', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Stripe billing config',
                'verbose_name_plural': 'Stripe billing config',
            },
        ),
    ]
