
import sys
import datetime
import dateparser
from health_stats.models.events import Event


class DateRange(object):

    __slots__ = (
        'start',
        'end',
        'tz',
    )

    @staticmethod
    def _parse_date(date, default):
        if isinstance(date, (datetime.date, datetime.datetime)):
            return date
        if date:
            try:
                return dateparser.parse(date)
            except Exception:
                print "Couldn't parse date: {}".format(date)
                sys.exit(1)
        return default

    def __init__(self, start, end, tz=None):
        self.start = self._parse_date(start, datetime.datetime.min)
        self.end = self._parse_date(end, datetime.datetime.max)
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
