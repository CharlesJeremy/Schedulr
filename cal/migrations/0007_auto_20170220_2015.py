# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-20 20:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0006_event_event_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.PositiveIntegerField(choices=[('', '(None)'), (1, 'Class'), (2, 'Social'), (3, 'Exercise'), (4, 'Shower'), (5, 'Meal')], null=True),
        ),
    ]
