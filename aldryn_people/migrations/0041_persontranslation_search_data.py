# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-26 16:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0040_group_sorting'),
    ]

    operations = [
        migrations.AddField(
            model_name='persontranslation',
            name='search_data',
            field=models.TextField(blank=True, editable=False),
        ),
    ]
