# Generated manually — remove TV catalog models (Data Center is downloads-only).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auditlog_is_archived'),
    ]

    operations = [
        migrations.DeleteModel(name='TVModel'),
        migrations.DeleteModel(name='TVBrand'),
    ]
