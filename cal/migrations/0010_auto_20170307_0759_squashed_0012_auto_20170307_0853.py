# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-07 09:01
from __future__ import unicode_literals

import annoying.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [(b'cal', '0010_auto_20170307_0759'), (b'cal', '0011_auto_20170307_0852'), (b'cal', '0012_auto_20170307_0853')]

    dependencies = [
        ('cal', '0009_smartschedulingprefs'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='dont_smart_schedule',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='event',
            name='smart_schedule_info',
            field=annoying.fields.JSONField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='smart_scheduled_for',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dependents', to='cal.Event'),
        ),
        migrations.AlterField(
            model_name='smartschedulingprefs',
            name='user',
            field=annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='scheduling_prefs', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
