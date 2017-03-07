from datetime import timedelta

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from cal.models import Event
from .utils import exercise_blocks


@transaction.atomic
def reset_shower_scheduling_for_exercise(exercise_event):
    """ Take event under the control of smart scheduling. """
    if exercise_event.dont_smart_schedule:
        exercise_event.dont_smart_schedule = False
        exercise_event.save()

        dependents = list(exercise_event.dependents.all())
        for dependent_event in dependents:
            if (dependent_event.smart_schedule_info and
                    dependent_event.smart_schedule_info.get('type') == 'shower_exercise'):
                # We don't need it any more.
                # TODO(zhangwen): is it really a good idea to remove a shower event that has been
                # operated on by the user?
                dependent_event.delete()


@receiver(post_save, sender=Event)
def update_dependent_events(sender, instance, **kwargs):
    """ Updates dependent events (e.g. shower for exercise). """
    for dependent_event in instance.dependents.all():
        dependent_event.update_by_delta()


@receiver(post_save, sender=Event)
def update_exercise_block_smart_scheduling(sender, instance, **kwargs):
    """ If this exercise event makes some other exercise events part of a block, remove their
    scheduled showers. """
    if instance.event_type != Event.EXERCISE:
        return

    # TODO(zhangwen): this is not very efficient.
    all_exercise_events = list(Event.objects.filter(user=instance.user, event_type=Event.EXERCISE))
    for exercise_block in exercise_blocks(all_exercise_events):
        for exercise_event in exercise_block[:-1]:
            # exercise_event is in the middle of an event block; remove its scheduled shower.
            reset_shower_scheduling_for_exercise(exercise_event)

