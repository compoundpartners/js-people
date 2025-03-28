# Generated by Django 3.2.25 on 2025-03-24 17:07

import cms.models.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('aldryn_people', '0052_person_locations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='placeholder_sidebar',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, slotname='person_sidebar', to='cms.placeholder'),
        ),
    ]
