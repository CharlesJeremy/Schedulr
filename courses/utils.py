class Quarter:
    """ An 'enum' for the four quarters of the year. """
    AUTUMN = 0
    WINTER = 1
    SPRING = 2
    SUMMER = 3

    # CHOICES can be used in Django model field as `choices`.
    CHOICES = (
            (AUTUMN, 'Autumn'),
            (WINTER, 'Winter'),
            (SPRING, 'Spring'),
            (SUMMER, 'Summer'),
    )

    STR_TO_VAL = { string: value for (value, string) in CHOICES }

    @staticmethod
    def parse(quarter_str):
        return Quarter.STR_TO_VAL[quarter_str]


class DaysOfWeek(object):
    """ Represents an immutable set of days of the week, e.g. [ Mon, Tue, Fri ]. """

    # Matches Python's datetime.datetime convention.
    STR_TO_VAL = {
            'mon': 0,
            'tue': 1,
            'wed': 2,
            'thu': 3,
            'fri': 4,
            'sat': 5,
            'sun': 6,
    }
    VAL_TO_STR = dict(zip(xrange(7), ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')))

    def __day_str_to_val(self, day_str):
        """ Turns string (e.g. 'Mon') into value (e.g. 0).  Raises ValueError on invalid string.
        """
        value = self.STR_TO_VAL.get(day_str.strip().lower())
        if value is None:
            print(day_str.strip().lower())
            raise ValueError(u'"%s" is not a day of the week' % day_str.strip())
        return value

    def __init__(self, ds):
        """
        `ds` can be:
            - a comma-delimited string, e.g. 'Mon, Tue, Fri',
            - a list of strings, e.g. ['Mon', 'Tue', 'Fri'],
            - or an integer returned by `to_int`.

        Raises ValueError when `ds` is not valid.
        """
        self.days = set()  # Subset of {0,1,2,3,4,5,6}.

        if isinstance(ds, basestring):
            for day_str in ds.split(','):
                self.days.add(self.__day_str_to_val(day_str))
        elif isinstance(ds, list):
            for day_str in ds:
                self.days.add(self.__day_str_to_val(day_str))
        elif isinstance(ds, int):
            for i in range(7):
                if ds & (1 << i):
                    self.days.add(i)
        else:
            raise ValueError(u"DaysOfWeek doesn't accept `ds` of type %s" % type(ds))

    def to_int(self):
        """ Returns integer representing set. """
        val = 0
        for day in self.days:
            val += (1 << day)
        return val

    def __contains__(self, d):
        """ `d` is either a string (e.g. 'Mon') or a number (e.g. 0 for Monday). """
        if isinstance(d, str):
            return (self.STR_TO_VAL[d.strip().lower()] in self.days)
        else:
            assert isinstance(d, int)
            return (d in self.days)

    def __unicode__(self):
        return ', '.join(self.VAL_TO_STR[val] for val in sorted(self.days))

