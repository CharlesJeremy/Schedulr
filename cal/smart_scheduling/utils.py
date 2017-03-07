import datetime
from datetime import timedelta

from cal.models import Event


def exercise_blocks(events):
    """
    Yields list of events in each exercise block.

    `events` is a list.
    """
    events.sort(key=lambda e: (e.start_time, e.end_time))

    exercise_block = []
    block_start_event = None
    block_end_event = None

    events_with_dummy_exercise = events + [Event(event_type=Event.EXERCISE,
        start_time=datetime.datetime.max, end_time=datetime.datetime.max)]

    for event in events_with_dummy_exercise:
        if event.event_type != Event.EXERCISE:
            continue

        if not exercise_block:
            exercise_block.append(event)
        elif event.start_time - exercise_block[-1].end_time <= timedelta(hours=1):
            # Put the current event in the same exercise block.
            exercise_block.append(event)
        else:
            yield exercise_block
            # Start a new exercise block.
            exercise_block = [event]

