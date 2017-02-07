import datetime
from datetime import timedelta
from functools import wraps
import re
import simplejson

import dateutil.parser
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .models import Event
from courses.models import Course, Section
from courses.utils import Quarter

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

def add_all_events_for_course(user, user_input):
    course = get_course(user_input);
    if course is None:
        return
    term = get_term()
    sections = get_sections(course, term)
    events = []
    for section in sections:
        events += add_section_events(user, course, section)
    return events

def get_term():
    # Hardcoded for now 
    return (2016, Quarter.WINTER)

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

def get_sections(course, term):
    """ Given a valid course object and term year/quarter, gets the related
    sections from the database """
    term_year = term[0]
    term_quarter = term[1]
    result = Section.objects.filter(course = course, term_year = term_year,
            term_quarter = term_quarter)
    return list(result)

def daterange(start_date, end_date):
    """ Taken from
    http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python """
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def add_section_events(user, course, section):
    """ Given a user and section object, adds and returns all relevant 
    events for the quarter to the database """
    try:
        schedule = section.schedule
    except: # TODO(zhangwen): proper exception
        return []

    events = []
    for date in daterange(schedule.start_date, schedule.end_date):
        if date.weekday() in schedule.days_of_week:
            Event.objects.create(
                    course=course, user=user,
                    name=unicode(course),
                    location=schedule.location,
                    start_time=datetime.datetime.combine(date, schedule.start_time),
                    end_time=datetime.datetime.combine(date, schedule.end_time))

    return events

# --- VIEWS ---
@login_required
@never_cache
def index(request):
    return render(request, 'cal/cal.html')

@login_required
@require_POST
def add_course(request):
    # TODO(zhangwen): proper error message.
    course_str = request.POST['event_title'] # TODO(zhangwen): call it sth else
    add_all_events_for_course(request.user, course_str)
    return redirect('/')

@ajax_login_required
def get_event_feed(request):
    start = request.GET.get('start')
    if start is None:
        return HttpJsonResponseBadRequest("\"start\" param missing.")
    try:
        start_dt = dateutil.parser.parse(start) # datetime
    except (ValueError, OverflowError) as e:
        return HttpJsonResponseBadRequest("\"start\" param invalid: %s." % e)

    end = request.GET.get('end')
    if end is None:
        return HttpJsonResponseBadRequest("\"end\" param missing.")
    try:
        end_dt = dateutil.parser.parse(end) # datetime
    except (ValueError, OverflowError) as e:
        return HttpJsonResponseBadRequest("\"end\" param invalid: %s." % e)

    # Maps Course id to Event id.
    # This map exists because events in the same series should have the same id.
    # If an Event is standalone, then just use its id.  If it's associated with a Course, use the
    # id of the first Event in that series (stored in this map).
    # TODO(zhangwen): this isn't pretty; we should probably have an event_id field.
    course_event_ids = {}

    events = Event.objects.filter(Q(user=request.user),
            Q(start_time__range=(start_dt, end_dt)) | Q(end_time__range=(start_dt, end_dt)))
    json_events = []
    for event in events:
        # See comment for course_event_ids.
        if event.course is not None:
            course = event.course
            if course.id not in course_event_ids:
                first_event_for_course = Event.objects.filter(course=course).order_by('id').first()
                course_event_ids[course.id] = first_event_for_course.id

            event_id = course_event_ids[course.id]
        else:
            event_id = event.id

        json_event = {
                'id': event_id,
                'title': event.name,
                'start': event.start_time.isoformat(),
                'end': event.end_time.isoformat()
        }
        json_events.append(json_event)

    json = simplejson.dumps(json_events)
    return HttpResponse(json, content_type='application/json')

@require_POST
@ajax_login_required
def add_event(request):
    title = request.POST.get('title')
    if not title:
        return HttpJsonResponseBadRequest("\"title\" param missing.")

    # TODO(zhangwen): de-duplicate this?
    start = request.POST.get('start')
    if start is None:
        return HttpJsonResponseBadRequest("\"start\" param missing.")
    try:
        start_dt = dateutil.parser.parse(start) # datetime
    except (ValueError, OverflowError) as e:
        return HttpJsonResponseBadRequest("\"start\" param invalid: %s." % e)

    end = request.POST.get('end')
    if end is None:
        return HttpJsonResponseBadRequest("\"end\" param missing.")
    try:
        end_dt = dateutil.parser.parse(end) # datetime
    except (ValueError, OverflowError) as e:
        return HttpJsonResponseBadRequest("\"end\" param invalid: %s." % e)

    # TODO(zhangwen): error handling, e.g. title too long.
    Event.objects.create(user=request.user, name=title, start_time=start_dt, end_time=end_dt)

    json = simplejson.dumps({'success': 'true'})
    return HttpResponse(json, content_type='application/json')
