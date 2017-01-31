from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
import re
from courses.models import Course

@login_required
def index(request):
    return HttpResponse("Front page!")

def get_course(user_string):
    """ Given a user string such as CS194, gets the course object
    from the database; also handles variations such as CS 194 and cs194"""
    user_string.replace(" ", "");
    index = re.search("\d", user_string).start();
    subject = user_string[:index].upper()
    code = user_string[index:].upper()
    result = Course.objects.filter(subject = subject, code = code)
    return result
