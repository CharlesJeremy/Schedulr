from __future__ import unicode_literals

from django.db import models

from courses.models import Course
from django.contrib.auth.models import User

class Event(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 200)
    description  = models.TextField()
    location = models.CharField(max_length = 200)
    start_time = models.TimeField()
    end_time = models.TimeField()
