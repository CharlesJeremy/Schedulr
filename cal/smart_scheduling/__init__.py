import datetime
from datetime import timedelta

import simplejson

from cal.models import Event
from cal.utils import daterange
from cal.smart_scheduling.utils import exercise_blocks
import cal.smart_scheduling.signals


BED_TIME_LIMIT = datetime.time(hour=3)
EDITABLE_SCHEDULE_TYPES = ['shower_exercise']


def _schedule_showers(prefs, start_dt, end_dt, events):
    """ Schedules shower events for user. """
    shower_events_exercise = [] # List of Event objects.
    shower_events_bed = [] # List of Event objects.

    # User preferences.
    exercise_shower_delta = prefs.exercise_shower_delta
    exercise_shower_duration = prefs.exercise_shower_duration

    today = datetime.date.today()
    bed_shower_start_time = prefs.bed_shower_start_time
    bed_shower_duration = datetime.datetime.combine(today, prefs.bed_shower_end_time) - \
        datetime.datetime.combine(today, bed_shower_start_time)

    # First, schedule a showers after each exercise block.
    for exercise_block in exercise_blocks(events):
        block_start_event, block_end_event = exercise_block[0], exercise_block[-1]
        if not block_end_event.dont_smart_schedule:
            # The previous exercise block has ended; schedule a shower.
            # TODO(zhangwen): what if there's a conflict?
            shower_start_time = block_end_event.end_time + exercise_shower_delta
            shower_event = Event(name="Shower (exercise)",
                    start_time=shower_start_time,
                    end_time=shower_start_time + exercise_shower_duration,
                    event_type=Event.SHOWER,
                    smart_scheduled_for=block_end_event)
            shower_events_exercise.append(shower_event)

    # Then, schedule before-bed shower (at most one per day).
    # By default it takes place at 10pm, but it is postponed if there are events after 10pm.
    for date in daterange(start_dt, end_dt):
        # Find last event before bed.
        bed_time_limit = datetime.datetime.combine(date + timedelta(days=1), BED_TIME_LIMIT)
        events_before_bed = [(i, e) for i, e in enumerate(events) if e.start_time <=
                bed_time_limit]
        if events_before_bed:
            last_event_of_day_idx, last_event_of_day = max(events_before_bed,
                    key=lambda (_, e): e.start_time)
            if last_event_of_day.end_time.date() >= date:
                if last_event_of_day_idx < len(events) - 1:
                    next_event = events[last_event_of_day_idx+1]
                    if next_event.start_time - last_event_of_day.end_time < timedelta(hours=5):
                        # Not sure when this day ends...  give up on scheduling bed time shower.
                        continue

            shower_start_dt = max(last_event_of_day.end_time, datetime.datetime.combine(date,
                bed_shower_start_time))
        else:
            shower_start_dt = datetime.datetime.combine(date, bed_shower_start_time)

        # Make sure you haven't showered too recently already.
        prev_showers = [e for e in events + shower_events_exercise + shower_events_bed
                if e.event_type == Event.SHOWER and e.start_time <= shower_start_dt]
        if prev_showers:
            prev_shower = max(prev_showers, key=lambda e: e.end_time)
            if shower_start_dt - prev_shower.end_time < timedelta(hours=5):
                continue

        shower_event = Event(name="Shower (bed time)", start_time=shower_start_dt,
                end_time=shower_start_dt + bed_shower_duration, event_type=Event.SHOWER)
        shower_events_bed.append(shower_event)

    shower_event_dicts = []
    for shower_for_exercise in shower_events_exercise:
        event_dict = shower_for_exercise.to_dict()
        event_dict.update({
            'schedule_type': 'shower_exercise',
            'smart_id': shower_for_exercise.smart_scheduled_for.id,
        })
        shower_event_dicts.append(event_dict)

    for shower_bed in shower_events_bed:
        event_dict = shower_bed.to_dict()
        event_dict.update({
            'schedule_type': 'shower_bed'
        })
        shower_event_dicts.append(event_dict)

    return shower_event_dicts


def schedule(user, start_dt, end_dt, events):
    """
    Returns a JSON list of smart-scheduled events based on existing events and user's preferences.
    """
    scheduled_event_dicts = []
    scheduled_event_dicts.extend(_schedule_showers(
        user.scheduling_prefs, start_dt, end_dt, events))

    # Assign dummy ids to smart-scheduled events.
    for i, d in enumerate(scheduled_event_dicts):
        d['id'] = -(i + 1)
        if d['schedule_type'] not in EDITABLE_SCHEDULE_TYPES:
            d['editable'] = False

    return simplejson.dumps(scheduled_event_dicts)


def update_smart_scheduling_prefs(event, duration_changed=True, time_changed=True):
    """ Updates user's smart scheduling preferences, if applicable. """
    # For showers scheduled for exercises.
    if (event.smart_schedule_info and event.smart_schedule_info.get('type') ==
            'shower_exercise'):
        prefs = event.user.scheduling_prefs

        delta_to_exercise = timedelta(seconds=event.smart_schedule_info['delta_s'])
        shower_duration = event.end_time - event.start_time

        # Process delta_to_exercise.
        if time_changed:
            if delta_to_exercise != prefs.exercise_shower_delta:
                if delta_to_exercise == prefs.candidate_exercise_shower_delta:
                    # Happened twice, save it.
                    prefs.exercise_shower_delta = delta_to_exercise
            prefs.candidate_exercise_shower_delta = delta_to_exercise

        # Process shower_duration
        if duration_changed:
            if shower_duration != prefs.exercise_shower_duration:
                if shower_duration == prefs.candidate_exercise_shower_duration:
                    # Happened twice, save it.
                    prefs.exercise_shower_duration = shower_duration
            prefs.candidate_exercise_shower_duration = shower_duration

        prefs.save()

