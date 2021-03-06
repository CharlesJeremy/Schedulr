# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-07 06:28
from __future__ import unicode_literals

import annoying.fields
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('cal', '0008_event_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmartSchedulingPrefs',
            fields=[
                ('user', annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('exercise_shower_delta', models.DurationField(default=datetime.timedelta(0))),
                ('exercise_shower_duration', models.DurationField(default=datetime.timedelta(0, 1800))),
            ],
        ),
    ]
