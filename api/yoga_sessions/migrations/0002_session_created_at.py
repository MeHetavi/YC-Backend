# Generated by Django 5.1 on 2025-01-30 04:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yoga_sessions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
