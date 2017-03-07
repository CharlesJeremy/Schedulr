from __future__ import unicode_literals
from datetime import timedelta

from django.db import models

from annoying.fields import AutoOneToOneField

from courses.models import Section
from django.contrib.auth.models import User

class Event(models.Model):
    """ An event in the calendar.  A repeated event is modeled as multiple Event objects. """
    DEFAULT = ''
    CLASS = 1
    SOCIAL = 2
    EXERCISE = 3
    SHOWER = 4
    MEAL = 5
    EVENT_TYPE_CHOICES = (
            (DEFAULT, "(None)"),
            (CLASS, "Class"),
            (SOCIAL, "Social"),
            (EXERCISE, "Exercise"),
            (SHOWER, "Shower"),
            (MEAL, "Meal"),
    )
    EVENT_TYPE_TO_STRING = dict(EVENT_TYPE_CHOICES)

    section = models.ForeignKey(Section, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 200)
    description  = models.TextField(blank=True, null=True)
    location = models.CharField(max_length = 200, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event_type = models.PositiveIntegerField(choices=EVENT_TYPE_CHOICES, null=True)
    color = models.CharField(max_length=25, default='red')

    def to_dict(self):
        """ To jsonify Event. """
        json_event = {
                'title': self.name,
                'start': self.start_time.isoformat(),
                'end': self.end_time.isoformat(),
                'event_type': self.event_type or None,
                'color': self.color
        }
        if self.id is not None:
            json_event['id'] = self.id
        if self.event_type:
            json_event['className'] = self.EVENT_TYPE_TO_STRING[self.event_type]
        return json_event


class SmartSchedulingPrefs(models.Model):
    """
    Auto-scheduling preferences for a User.

    Every field of this model MUST either be nullable or have a default value.
    """
    user = AutoOneToOneField(User, on_delete=models.CASCADE, primary_key=True,
            related_name='scheduling_prefs')

    # Duration between end of exercise and beginning of scheduled shower.
    # Defaults to immediately after exercise.
    exercise_shower_delta = models.DurationField(default=timedelta())

    # Duration of exercise shower.  Defaults to 30 minutes.
    exercise_shower_duration = models.DurationField(default=timedelta(minutes=30))
