from __future__ import unicode_literals
import itertools

from django.db import models

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

    def to_dict(self):
        """ To jsonify Event. """
        json_event = {
                'title': self.name,
                'start': self.start_time.isoformat(),
                'end': self.end_time.isoformat(),
                'event_type': self.event_type or None,
        }
        if self.id is not None:
            json_event['id'] = self.id
        if self.event_type:
            json_event['className'] = self.EVENT_TYPE_TO_STRING[self.event_type]
        return json_event
