from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models

from .utils import Quarter, DaysOfWeek


class Course(models.Model):
    """ A Stanford course (e.g. CS 194). """
    subject = models.CharField(max_length=10) # e.g. "CS".
    code = models.CharField(max_length=10) # e.g. "194W".
    title = models.CharField(max_length=200) # e.g. "Software Project (WIM)".

    class Meta:
        ordering = ('subject', 'code')

    def __unicode__(self):
        return '%s %s: %s' % (self.subject, self.code, self.title)


class DaysOfWeekField(models.Field):
    """
    A field representing a set of days of the week, e.g. { Mon, Fri }.
    
    This field is backed by the DaysOfWeek Python class.
    """
    description = "Set of days of the week"

    def get_internal_type(self):
        return "PositiveIntegerField"

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value

        try:
            return DaysOfWeek(value)
        except ValueError as e:
            raise ValidationError(e)

    def to_python(self, value):
        if isinstance(value, DaysOfWeek):
            return value

        if value is None:
            return value

        try:
            return DaysOfWeek(value)
        except ValueError as e:
            raise ValidationError(e)

    def get_prep_value(self, value):
        assert isinstance(value, DaysOfWeek)
        return value.to_int()

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        assert isinstance(value, DaysOfWeek)
        return value.to_int()

    def formfield(self, **kwargs):
        from django.forms import CharField
        defaults = { 'form_class': CharField }
        defaults.update(kwargs)
        return super(DaysOfWeekField, self).formfield(**defaults)


class Section(models.Model):
    """ A section for a course, in a particular term (e.g. Winter 2016-2017). """
    course = models.ForeignKey(Course, on_delete=models.CASCADE) # Course that section belongs to.
    class_id = models.IntegerField() # e.g. 32092.
    term_year = models.IntegerField("Academic year") # e.g. 2016 for the 2016-17 academic year.
    term_quarter = models.IntegerField("Quarter", choices=Quarter.CHOICES) # e.g. `Quarter.WINTER`.
    section_number = models.IntegerField() # e.g. 1.
    component = models.CharField(max_length=3) # e.g. "LEC".
    instructors = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        ordering = ('term_year', 'term_quarter')


class Schedule(models.Model):
    """
    Schedule for a section.
    
    A section might not have a schedule (e.g. CS 199), but a schedule must belong to exactly one
    section.
    """
    section = models.OneToOneField(Section, on_delete=models.CASCADE, primary_key=True)
    start_date = models.DateField() # e.g. 2017/1/9.
    end_date = models.DateField() # e.g. 2017/3/17.
    days_of_week = DaysOfWeekField()
    start_time = models.TimeField() # e.g. 13:30.
    end_time = models.TimeField() # e.g. 14:50.
    location = models.CharField(max_length=100, null=True, blank=True) # e.g. "School of Education 334".

    def __unicode__(self):
        str_repr = "%s--%s | %s %s--%s" % (self.start_date, self.end_date, self.days_of_week,
                self.start_time, self.end_time)
        if self.location:
            str_repr += " | %s" % self.location

        return str_repr

