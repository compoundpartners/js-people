# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-06-19 05:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0018_auto_20160802_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='facebook',
            field=models.URLField(blank=True, null=True, verbose_name='facebook'),
        ),
        migrations.AddField(
            model_name='person',
            name='linkedin',
            field=models.URLField(blank=True, null=True, verbose_name='linkedin'),
        ),
        migrations.AddField(
            model_name='person',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='location'),
        ),
        migrations.AddField(
            model_name='person',
            name='twitter',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='twitter'),
        ),
    ]
