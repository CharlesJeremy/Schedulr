# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-14 11:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0011_auto_20170307_1033_squashed_0012_auto_20170307_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='smartschedulingprefs',
            name='bed_shower_time',
            field=models.TimeField(default=datetime.time(22, 0)),
        ),
    ]
