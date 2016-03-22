
"""
health-stats
====
"""

from collections import namedtuple, OrderedDict

import numpy
from pretty import pprint

__version__ = '0.0.1'


InsulinData = namedtuple('InsulinValues', ['basal', 'meal', 'correction'])

MealData = namedtuple('MealValues', ['carbs', 'description'])


class HealthStats(object):

    __slots__ = (
        'log',
        'days',
    )

    def __init__(self):
        self.log = EventLog()
        self.days = OrderedDict()

    def extend(self, events):
        self.log.extend(events)

    def analyze(self):
        self.log.sort()
        self.days = OrderedDict()
        for event in self.log.events:
            # Add this event to the group-by-days entries
            day = event.event_time.date()
            if day not in self.days:
                self.days[day] = EventLog()
            self.days[day].add(event)
            # @todo group by other time periods?

    def __pretty__(self, p, cycle):
        p.text('<{0}: '.format(type(self).__name__))
        if cycle:
            p.text('...')
        else:

            p.pretty({
                'log': self.log,
                'days': self.days.keys(),
            })
        p.text('>')


class EventLog(object):

    __slots__ = ('events')

    def __init__(self):
        self.events = []

    def sort(self):
        self.events.sort()

    def add(self, event):
        self.events.append(event)

    def extend(self, events):
        self.events.extend(events)

    def glucose_values(self):
        values = []
        for event in self.events:
            if event.glucose:
                values.append(event.glucose)
        return values

    def glucose_mean(self):
        values = self.glucose_values()
        if len(values) > 0:
            return '{0:.0f}'.format(numpy.mean(values))
        return None

    def glucose_std(self):
        values = self.glucose_values()
        if len(values) > 0:
            return '{0:.0f}'.format(numpy.std(values))
        return None

    def __pretty__(self, p, cycle):
        p.text('<{0}: '.format(type(self).__name__))
        if cycle:
            pass
        else:
            p.pretty({
                'events': self.events,
            })
        p.text('>')


class LogEvent(object):
    """ A single log entry """

    __slots__ = (
        'event_time',
        'glucose',
        'insulin',
        'meal',
        'note',
        'location',
        'tags',
        'bp_systolic',
        'bp_diastolic',
        'weight_lbs',
    )

    def __init__(self, event_time, glucose=None, insulin=None, meal=None, note=None, location=None, tags=None, bp_systolic=None, bp_diastolic=None, weight_lbs=None):
        self.event_time = event_time
        self.glucose = int(glucose) if glucose is not None else None
        self.insulin = insulin or InsulinData(None, None, None)
        self.meal = meal or MealData(None, None)
        self.location = location
        self.note = note
        self.tags = tuple(tags)
        # @todo other values...

    def __cmp__(self, other):
        if isinstance(other, LogEvent):
            return cmp(self.event_time, other.event_time)
        try:
            return cmp(self.event_time, other)
        except TypeError as e:
            # print("Can't compare {} to {}".format(self, other))
            raise e

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __pretty__(self, p, cycle):
        p.text('<{0}: '.format(type(self).__name__))
        if cycle:
            p.text(str(self.event_time))
        else:
            p.text(', '.join([str(self.event_time), str(self.glucose)]))
        p.text('>')
