from bs4 import BeautifulSoup
import datetime
import os
import pickle
import re
import urllib2

from .course_objects import *

XML_FILE = 'courses/scraper/courses.xml'
XML_URL = r'http://explorecourses.stanford.edu/search?view=xml&filter-coursestatus-Active=on&page=0&academicYear=&q=%'
HTML_FILE = 'courses/scraper/courses.html'
HTML_URL = r'http://explorecourses.stanford.edu/print?filter-coursestatus-Active=on&schedules=on&q=%'

def parse_term(term_str):
    """
    Returns Term object corresponding to `term_str`, a string of format '2016-2017 Winter'.
    """
    match_obj = re.match(r'(\d{4})-(\d{4}) (Autumn|Winter|Spring|Summer)', term_str)
    assert match_obj
    year = int(match_obj.group(1))
    assert year + 1 == int(match_obj.group(2))
    return Term(year, quarter=match_obj.group(3))

def get_data(url, filename=None):
    """
    If `filename` exists (and not None), returns its contents.  Otherwise, fetches from `url`,
    stores contents in `filename`, and returns contents.
    """
    if (filename is None) or (not os.path.exists(filename)):
        data = urllib2.urlopen(url).read()
        if filename is not None:
            with open(filename, "w") as f:
                f.write(data)
        return data
    else:
        with open(filename, "r") as f:
            return f.read()

def parse_section_details(s):
    """
    If a section schedule can be constructed from sectionDetails tag `s`, returns pair
    ((course_subj, course_code, term, class_id), schedule).  Otherwise, returns None.
    """
    class_id_pattern = re.compile(r'Class # (\d+)')
    schedule_pattern = re.compile((
        r'(?P<start_date>\d{2}/\d{2}/\d{4}) - (?P<end_date>\d{2}/\d{2}/\d{4}) '
        r'(?P<days_of_week>(Mon|Tue|Wed|Thu|Fri|Sat|Sun)(, (Mon|Tue|Wed|Thu|Fri|Sat|Sun))*) '
        r'(?P<start_time>(\d+):(\d+) (AM|PM)) - (?P<end_time>(\d+):(\d+) (AM|PM))'
        r'( at (?P<location>.+) with)?'))

    # Find term.
    section_container_div = s.parent.parent
    assert 'sectionContainer' in section_container_div['class']
    term = parse_term(section_container_div.find(class_='sectionContainerTerm').get_text())

    details_str = s.get_text()
    details = details_str.split('|')
    course_subj, course_code = [w.strip() for w in details[0].split()]
    class_id = None
    for s in details:
        # Look for class id.
        class_id_match = re.search(class_id_pattern, s)
        if class_id_match:
            assert class_id is None
            class_id = int(class_id_match.group(1))

        # Look for schedule.
        schedule_match = re.search(schedule_pattern, s)
        if schedule_match:
            start_date_str = schedule_match.group('start_date')
            end_date_str = schedule_match.group('end_date')
            try:
                start_date = datetime.datetime.strptime(start_date_str, '%m/%d/%Y').date()
                end_date = datetime.datetime.strptime(end_date_str, '%m/%d/%Y').date()
            except ValueError:  # Invalid date format.
                continue

            days_of_week = schedule_match.group('days_of_week').split(', ')
            start_time_str = schedule_match.group('start_time')
            end_time_str = schedule_match.group('end_time')
            try:
                start_time = datetime.datetime.strptime(start_time_str, '%I:%M %p').time()
                end_time = datetime.datetime.strptime(end_time_str, '%I:%M %p').time()
            except ValueError: # Invalid time format.
                continue

            location = schedule_match.group('location')

            assert class_id is not None
            schedule = Schedule(
                    start_date=start_date,
                    end_date=end_date,
                    days_of_week=days_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    location=location
            )
            return (course_subj, course_code, term, class_id), schedule

    return None

def extract_course_schedules():
    """
    Returns a Dict mapping class_id to Schedule.
    """
    # course_html = get_data(HTML_URL, HTML_FILE)
    course_html = get_data(HTML_URL)
    soup = BeautifulSoup(course_html, 'lxml')
    schedules = {}  # class_id => Schedule.
    for s in soup.find_all('li', class_='sectionDetails'):
        parsed = parse_section_details(s)
        if parsed:
            key = parsed[0]
            # print(key)
            assert key not in schedules
            schedules[key] = parsed[1]

    print("Schedules parsed.")

    return schedules

def extract_courses():
    schedules = extract_course_schedules()

    # courses_xml = get_data(XML_URL, XML_FILE)
    courses_xml = get_data(XML_URL)
    soup = BeautifulSoup(courses_xml, 'lxml-xml')
    print("Other info parsed.")
    for c in soup.find_all('course'):
        subject = c.subject.get_text()
        code = c.code.get_text()
        sections = []
        course = Course(subject, code, c.title.get_text(), sections)
        for s in c.sections.find_all('section'):
            class_id = int(s.classId.get_text())
            term=parse_term(s.term.get_text())
            schedule = schedules.get((subject, code, term, class_id))
            sections.append(Section(
                class_id=class_id,
                term=term,
                section_number=int(s.sectionNumber.get_text()),
                component=s.component.get_text(),
                instructors=s.instructors.get_text(),
                schedule=schedule))
        yield course

def main():
    courses = list(extract_courses())
    pickle.dump(courses, open("courses.p", "wb"))
    # print('%s\t%d section(s)' % (course.code, len(course.sections)))

if __name__ == '__main__':
    main()
