from datetime import timedelta

from django import forms

from .models import Event


class IntervalSecondsField(forms.IntegerField):
    """ Python timedelta by seconds. """
    def to_python(self, value):
        value = super(IntervalSecondsField, self).to_python(value)
        if value is None:
            return None

        return timedelta(seconds=value)

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'start_time', 'end_time']

class EditEventFormDelta(forms.ModelForm):
    duration_delta = IntervalSecondsField(required=False)
    time_delta = IntervalSecondsField(required=False)

    class Meta:
        model = Event
        fields = ['name']

    def save(self, commit=True):
        raise NotImplemented
