# Generated by Django 2.2.28 on 2023-06-14 13:09

from django.db import migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('js_locations', '0013_auto_20211203_1325'),
        ('aldryn_people', '0051_auto_20220414_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='locations',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, null=True, related_name='people', to='js_locations.Location', verbose_name='locations'),
        ),
    ]
