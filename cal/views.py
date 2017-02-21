import datetime
from datetime import timedelta
from functools import wraps
import re
import simplejson

import dateutil.parser
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .forms import DateRangeForm, EventForm, EditEventFormDelta
from .models import Event
from .smart_scheduling import schedule as smart_schedule
from .utils import daterange
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
    user_input = user_input.replace(" ", "");
    search = re.search("\d", user_input)
    if search is None:
        return None
    index = search.start();
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
            term_quarter = term_quarter).order_by('section_number')
    return list(result)

def add_section_events(user, section):
    """ Given a user and section object, adds and returns all relevant 
    events for the quarter to the database """
    try:
        schedule = section.schedule
    except: # TODO(zhangwen): proper exception
        return []

    course = section.course
    events = []
    for date in daterange(schedule.start_date, schedule.end_date):
        if date.weekday() in schedule.days_of_week:
            Event.objects.create(
                    section=section, user=user,
                    name='[%s] %s' % (section.component, course),
                    location=schedule.location,
                    start_time=datetime.datetime.combine(date, schedule.start_time),
                    end_time=datetime.datetime.combine(date, schedule.end_time))

    return events

def get_events_in_range(user, start_dt, end_dt):
    """ Returns all Events for user within range [start_dt, end_dt), in ascending order by
    start_time. """
    return Event.objects.filter(Q(user=user),
            Q(start_time__range=(start_dt, end_dt)) | Q(end_time__range=(start_dt,
                end_dt))).order_by('start_time', 'end_time')


# --- VIEWS ---
@login_required
@never_cache
def index(request):
    event_form = EventForm()
    return render(request, 'cal/cal.html',
            context={ 'event_form': EventForm(),
                'event_type_choices': event_form.fields['event_type'].choices })

@login_required
@require_POST
@transaction.atomic
def add_sections(request):
    # TODO(zhangwen): error handling
    section_ids = map(int, request.POST.getlist('sections'))
    for section in Section.objects.filter(id__in=section_ids):
        add_section_events(request.user, section)
    return redirect('/')

@ajax_login_required
def get_sections_for_course(request):
    course_str = request.GET.get('course_str') # TODO(zhangwen): call it sth else
    if course_str is None:
        return HttpJsonResponseBadRequest("\"course_str\" param missing.")

    course = get_course(course_str);
    if course is None:
        json = simplejson.dumps({'error': 'No course found.'})
        return HttpResponse(json, content_type='application/json')

    sections_list = []
    sections = get_sections(course, get_term())
    for section in sections:
        try:
            schedule = section.schedule
        except: # TODO(zhangwen): proper exception
            continue

        sections_list.append({
            'section_id': section.id,
            'section_number': section.section_number,
            'component': section.component or "",
            'instructors': section.instructors or "",
            'schedule': unicode(schedule),
        })


    json = simplejson.dumps({
        'course_title': unicode(course),
        'sections': sections_list
    })
    return HttpResponse(json, content_type='application/json')

@ajax_login_required
def get_smart_scheduling_feed(request):
    form = DateRangeForm(request.GET)
    if not form.is_valid():
        return HttpJsonResponseBadRequest(form.errors)

    start_dt = form.cleaned_data['start']
    end_dt = form.cleaned_data['end']
    events = list(get_events_in_range(request.user, start_dt, end_dt))

    scheduled_events = smart_schedule(start_dt, end_dt, events)
    json_events = [e.to_dict() for e in scheduled_events]
    json = simplejson.dumps(json_events)
    return HttpResponse(json, content_type='application/json')

@ajax_login_required
def get_event_feed(request):
    form = DateRangeForm(request.GET)
    if not form.is_valid():
        return HttpJsonResponseBadRequest(form.errors)

    start_dt = form.cleaned_data['start']
    end_dt = form.cleaned_data['end']
    events = get_events_in_range(request.user, start_dt, end_dt)

    json_events = [e.to_dict() for e in events]
    json = simplejson.dumps(json_events)
    return HttpResponse(json, content_type='application/json')

@require_POST
@ajax_login_required
@transaction.atomic
def delete_event(request, event_id):
    """ Removes all events in the series that Event `event_id` belongs to. """
    event = get_object_or_404(Event, user=request.user, id=int(event_id))
    section = event.section
    if section is None: # Just delete this event.
        event.delete()
    else: # Delete all events associated with this section.
        Event.objects.filter(user=request.user, section=section).delete()

    json = simplejson.dumps({'success': 'true'})
    return HttpResponse(json, content_type='application/json')

@require_POST
@ajax_login_required
def add_event(request):
    form = EventForm(request.POST)
    if not form.is_valid():
        return HttpJsonResponseBadRequest(form.errors)

    event = form.save(commit=False)
    event.user = request.user
    event.save()

    json = simplejson.dumps({'success': 'true', 'id': event.id})
    return HttpResponse(json, content_type='application/json')

@require_POST
@ajax_login_required
@transaction.atomic
def edit_event_abs(request, event_id):
    """ Updates all events in the series that Event `event_id` belongs to using absolute times. """
    event = get_object_or_404(Event, user=request.user, id=int(event_id))
    form = EventForm(request.POST, instance=event)
    if not form.is_valid():
        return HttpJsonResponseBadRequest(form.errors)

    section = event.section
    if section is None: # Just update this event.
        form.save()
    else: # Update all events associated with this section.
        new_start_time = form.cleaned_data['start_time']
        new_end_time = form.cleaned_data['end_time']
        new_dt = new_end_time - new_start_time
        new_name = form.cleaned_data['name']
        for event in Event.objects.filter(user=request.user, section=section):
            event.name = new_name
            event.start_time = datetime.datetime.combine(
                    event.start_time.date(), new_start_time.time())
            event.end_time = event.start_time + new_dt
            event.event_type = form.cleaned_data['event_type']
            event.save()

    json = simplejson.dumps({'success': 'true'})
    return HttpResponse(json, content_type='application/json')

@require_POST
@ajax_login_required
@transaction.atomic
def edit_event_rel(request, event_id):
    """
    Updates all events in the series that Event `event_id` belongs to using relative times.
    """
    event = get_object_or_404(Event, user=request.user, id=event_id)

    form = EditEventFormDelta(request.POST)
    if not form.is_valid():
        return HttpJsonResponseBadRequest(form.errors)
    duration_delta = form.cleaned_data['duration_delta'] or timedelta()
    time_delta = form.cleaned_data['time_delta'] or timedelta()

    section = event.section
    if section is None:
        events = [event]
    else:
        events = Event.objects.filter(user=request.user, section=section)

    for event in events:
        old_duration = event.end_time - event.start_time
        event.start_time += time_delta
        event.end_time = event.start_time + old_duration + duration_delta
        event.save()

    json = simplejson.dumps({'success': 'true'})
    return HttpResponse(json, content_type='application/json')

