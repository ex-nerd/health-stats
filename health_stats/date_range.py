
import datetime
from health_stats.models.events import Event


class DateRange(object):

    __slots__ = (
        'start',
        'end',
        'tz',
    )

    def __init__(self, start, end, tz=None):
        self.start = start or datetime.datetime.min
        self.end = end or datetime.datetime.max
        self.tz = tz

    def __contains__(self, other):
        if other is None:
            return False
        if isinstance(other, (datetime.datetime, Event)):
            # @todo support timezones
            return (other >= self.start and other <= self.end)
        else:
            raise ValueError('DateRange can only contain datetime.datetime values (!= {})'.format(other))

    def __pretty__(self, p, cycle):
        p.text('<{0}: '.format(type(self).__name__))
        if cycle:
            pass
        else:
            p.text(repr({
                'start': self.start,
                'end': self.end,
                'tz': self.tz,
            }))
        p.text('>')
