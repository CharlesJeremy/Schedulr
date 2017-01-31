from __future__ import unicode_literals

from django.db import models

from courses.models import Course
from django.contrib.auth.models import User

class Event(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 200)
    description  = models.TextField(blank=True, null=True)
    location = models.CharField(max_length = 200, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
