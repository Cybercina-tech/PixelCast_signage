# Generated manually — model field existed without migration (caused 500 on /api/contents/).

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('templates', '0012_seed_sample_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='uploaded_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Account that uploaded this content (media library isolation)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='uploaded_contents',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name='content',
            index=models.Index(fields=['uploaded_by', 'widget'], name='templates_c_upload__a1b2c3_idx'),
        ),
    ]
