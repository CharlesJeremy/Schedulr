from collections import namedtuple
Course = namedtuple('Course', ['subject', 'code', 'title', 'sections'])

Section = namedtuple('Section', ['class_id', 'term', 'section_number', 'component', 'instructors',
    'schedule'])
Section.__new__.__defaults__ = (None,)  # `schedule` is optional.

Term = namedtuple('Term', ['year', 'quarter'])
Schedule = namedtuple('Schedule', ['start_date', 'end_date', 'days_of_week', 'start_time',
    'end_time', 'location'])
Schedule.__new__.__defaults__ = (None,)  # `location` is optional.
