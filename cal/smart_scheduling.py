import datetime
from datetime import timedelta

from .models import Event
from .utils import daterange


SHOWER_DURATION = timedelta(minutes=30)
DEFAULT_BED_SHOWER_TIME = datetime.time(hour=22)
BED_TIME_LIMIT = datetime.time(hour=3)


def _schedule_showers(start_dt, end_dt, events):
    """ Schedules shower events. """
    shower_events = []

    # First, schedule a showers after each exercise block.
    block_start_event = None
    block_end_event = None

    events_with_dummy_exercise = events + [Event(event_type=Event.EXERCISE,
        start_time=datetime.datetime.max, end_time=datetime.datetime.max)]

    for event in events_with_dummy_exercise:
        if event.event_type != Event.EXERCISE:
            continue

        if block_start_event is None:
            assert block_end_event is None
            block_start_event = block_end_event = event
        elif event.start_time - block_end_event.end_time <= timedelta(hours=1):
            # Put the current event in the same exercise block.
            block_end_event = event
        else:
            # The previous exercise block has ended; schedule a shower.
            # TODO(zhangwen): what if there's a conflict?
            shower_event = Event(name="Shower (exercise)", start_time=block_end_event.end_time,
                    end_time=block_end_event.end_time + SHOWER_DURATION,
                    event_type=Event.SHOWER)
            shower_events.append(shower_event)

            # Start a new exercise block.
            block_start_event = block_end_event = event

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
                DEFAULT_BED_SHOWER_TIME))
        else:
            shower_start_dt = datetime.datetime.combine(date, DEFAULT_BED_SHOWER_TIME)

        # Make sure you haven't showered too recently already.
        prev_showers = [e for e in events + shower_events
                if e.event_type == Event.SHOWER and e.start_time <= shower_start_dt]
        if prev_showers:
            prev_shower = max(prev_showers, key=lambda e: e.end_time)
            if shower_start_dt - prev_shower.end_time < timedelta(hours=2):
                continue

        shower_event = Event(name="Shower (bed time)", start_time=shower_start_dt,
                end_time=shower_start_dt + SHOWER_DURATION,
                event_type=Event.SHOWER)
        shower_events.append(shower_event)

    return shower_events


def schedule(start_dt, end_dt, events):
    """ Returns a list of smart-scheduled events based on existing events.
    
    `events` is sorted by (start_time, end_time).
    """
    scheduled_events = []
    scheduled_events.extend(_schedule_showers(start_dt, end_dt, events))
    return scheduled_events
