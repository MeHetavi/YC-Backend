# Generated by Django 5.1 on 2025-01-30 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yoga_sessions', '0003_rename_name_session_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='description',
            field=models.TextField(blank=True, max_length=10000),
        ),
    ]
