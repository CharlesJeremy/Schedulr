from datetime import timedelta

from django import forms

from .models import Event, SmartSchedulingPrefs


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
        fields = ['name', 'start_time', 'end_time', 'event_type', 'color']

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['event_type'].required = False

    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and (start_time > end_time):
            self.add_error('end_time', "End time must be later than start time.")

class EditEventFormDelta(forms.ModelForm):
    class Meta: # start_time and end_time fields might not be used.
        model = Event
        fields = ['start_time', 'end_time']

    duration_delta = IntervalSecondsField(required=False)
    time_delta = IntervalSecondsField(required=False)

    def save(self, commit=True):
        raise NotImplemented

class DateRangeForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()

class SmartSchedPrefsForm(forms.ModelForm):
    class Meta:
        model = SmartSchedulingPrefs
        fields = ['bed_shower_start_time', 'bed_shower_end_time']

    def __init__(self, *args, **kwargs):
        super(SmartSchedPrefsForm, self).__init__(*args, **kwargs)
        self.fields['bed_shower_start_time'].required = True
        self.fields['bed_shower_end_time'].required = True

    def clean(self):
        cleaned_data = super(SmartSchedPrefsForm, self).clean()
        bed_shower_start_time = cleaned_data.get('bed_shower_start_time')
        bed_shower_end_time = cleaned_data.get('bed_shower_end_time')
        if bed_shower_start_time and bed_shower_end_time and bed_shower_start_time > bed_shower_end_time:
            self.add_error('bed_shower_end_time', "End time must be later than start time.")

