from __future__ import unicode_literals
from datetime import timedelta

from django.db import models

from annoying.fields import AutoOneToOneField, JSONField

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

    # ----- Fields related to smart scheduling -----
    # If True, no event will be smart-scheduled based on this event.
    dont_smart_schedule = models.BooleanField(default=False, editable=False)
    # If this event is derived from a smart-scheduled event, this field is non-null and contains
    # information regarding smart scheduling (e.g. the type of scheduled event).  If this event is
    # just an ordinary event, this field is null.
    # TODO(zhangwen): document the schema.
    smart_schedule_info = JSONField(blank=True, null=True, editable=False)
    # If this event is derived from a smart-scheduled event and is scheduled based on another event
    # (e.g. shower time for exercise), this field points to the event it's associated with.
    smart_scheduled_for = models.ForeignKey('self', on_delete=models.CASCADE, blank=True,
            null=True, editable=False, related_name='dependents')

    def update_by_delta(self):
        """
        Update this event's times based on a time delta to the event it's associated with.  No-op
        if not applicable.
        """
        if (not self.smart_scheduled_for) or (not self.smart_schedule_info):
            # Doesn't depend on any other event.
            return

        delta_s = self.smart_schedule_info.get('delta_s')
        if delta_s is None: # Doesn't have a time delta.
            return

        delta_to_assoc_event = timedelta(seconds=delta_s)
        new_start_time = self.smart_scheduled_for.end_time + delta_to_assoc_event
        new_end_time = new_start_time + (self.end_time - self.start_time)

        self.start_time = new_start_time
        self.end_time = new_end_time
        self.save()

    def save(self, *args, **kwargs):
        # If a user makes certain changes to an event derived from an auto-scheduled event, turn
        # the event into just an ordinary event.
        if self.smart_schedule_info:
            smart_schedule_type = self.smart_schedule_info['type']
            if smart_schedule_type == 'shower_exercise':
                # For a shower event scheduled for an exercise, if the event is no longer of type
                # SHOWER, or if it's too far away (hard-coded 3 hours) from the exercise, or if
                # it starts before the exercise, then we turn it into an ordinary event.
                delta_to_exercise = self.start_time - self.smart_scheduled_for.end_time
                if ((self.event_type != Event.SHOWER) or (delta_to_exercise < timedelta()) or
                        (delta_to_exercise > timedelta(hours=3))):
                    self.smart_schedule_info = None
                    self.smart_scheduled_for = None

        # Record the delta between the auto-scheduled event and the event it's associated with, if
        # applicable.
        if self.smart_schedule_info and self.smart_scheduled_for:
            self.smart_schedule_info['delta_s'] =int((self.start_time -
                self.smart_scheduled_for.end_time).total_seconds())

        super(Event, self).save(*args, **kwargs)

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
        if self.smart_schedule_info:
            json_event['className'] = 'smart-scheduled-event'
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

    # Candidates; if the user specifies the same preference twice, that preference gets saved.
    candidate_exercise_shower_delta = models.DurationField(null=True, editable=False)
    candidate_exercise_shower_duration = models.DurationField(null=True, editable=False)

