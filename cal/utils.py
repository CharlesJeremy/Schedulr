import datetime
from datetime import timedelta

def daterange(start_date, end_date):
    """ Taken from
    http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python """
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def next_weekday(d, weekday):
    """
    Taken from
    http://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-a-date
    """
    days_ahead = weekday - d.weekday()
    if days_ahead < 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

