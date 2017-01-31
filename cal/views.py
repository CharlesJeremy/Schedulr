from functools import wraps
import re
import simplejson

import dateutil.parser
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from .models import Event
import re
from courses.models import Course, Section

class HttpResponseUnauthorized(HttpResponse):
    """
    Returned when user is not logged in for AJAX request.

    Is 401 really the right thing to return??  Meh...
    """
    status_code = 401

class HttpJsonResponseBadRequest(HttpResponseBadRequest):
    content_type = 'application/json'
    def __init__(self, msg, *args, **kwargs):
        super(HttpJsonResponseBadRequest, self).__init__(
            simplejson.dumps({ 'error': msg }),
            *args, **kwargs)

def ajax_login_required(view_func):
    """
    Taken from:
    http://stackoverflow.com/questions/312925/django-authentication-and-ajax-urls-that-require-login
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        json = simplejson.dumps({ 'error': "Not authenticated." })
        return HttpResponseUnauthorized(json, content_type='application/json')
    return wrapper

def add_all_events_for_course(user, user_input, term_year, term_quarter):
    course = get_course(user_input);
    if course is None:
        return
    sections = get_sections(course, term_year, term_quarter)
    events = []
    for section in sections:
        event += add_section_events(user, section)
    return events

def get_course(user_input):
    """ Given a user string such as CS194, gets the course object
    from the database; also handles variations such as CS 194 and cs194"""
    user_input.replace(" ", "");
    index = re.search("\d", user_input).start();
    subject = user_input[:index].upper()
    code = user_input[index:].upper()
    result = Course.objects.filter(subject = subject, code = code)
    if len(result) == 0:
        return None
    # Otherwise we assume there is only one matching course
    return result.get()

def get_sections(course, term_year, term_quarter):
    """ Given a valid course object and term year/quarter, gets the related
    sections from the database """
    result = Section.objects.filter(course = course, term_year = term_year,
            term_quarter = term_quarter)
    return list(result)
    

def add_section_event(user, section):
    """ Given a user and section object, adds and returns all relevant 
    events for the quarter to the database """
    events = []
    # TODO (rwang7) finish this
    return events

# --- VIEWS ---
@login_required
@never_cache
def index(request):
    return render(request, 'cal/cal.html')

@ajax_login_required
def get_event_feed(request):
    start = request.GET.get('start')
    if start is None:
        return HttpJsonResponseBadRequest("\"start\" param missing.")
    try:
        start_dt = dateutil.parser.parse(start) # datetime
        print(start_dt)
    except (ValueError, OverflowError) as e:
        return HttpJsonResponseBadRequest("\"start\" param invalid: %s." % e)

    end = request.GET.get('end')
    if end is None:
        return HttpJsonResponseBadRequest("\"end\" param missing.")
    try:
        end_dt = dateutil.parser.parse(end) # datetime
        print(end_dt)
    except (ValueError, OverflowError) as e:
        return HttpJsonResponseBadRequest("\"end\" param invalid: %s." % e)

    events = Event.objects.filter(Q(user=request.user),
            Q(start_time__range=(start_dt, end_dt)) | Q(end_time__range=(start_dt, end_dt)))
    json_events = []
    for event in events:
        json_event = {
                'title': event.name,
                'start': event.start_time.isoformat(),
                'end': event.end_time.isoformat()
        }
        if event.course is not None:
            json_event['id'] = event.course.id # Events in the same series should have the same id.
        json_events.append(json_event)

    json = simplejson.dumps(json_events)
    return HttpResponse(json, content_type='application/json')

