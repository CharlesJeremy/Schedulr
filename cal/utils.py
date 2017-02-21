from datetime import timedelta

def daterange(start_date, end_date):
    """ Taken from
    http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python """
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

