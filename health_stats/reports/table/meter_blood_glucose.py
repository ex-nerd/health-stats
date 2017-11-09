
# Python 2 and 3
from __future__ import print_function

import unicodecsv as csv
import sqlalchemy
from sqlalchemy import not_, or_

from ..report import Report

from health_stats.models.events import *
from health_stats.database import DBSession
from health_stats.dataset import DataSet

class MeterBloodGlucose(Report):

    def render(self, output):

        session = DBSession()
        events = session.query(GlucoseEvent)
        events = events.filter(Event.subtype == GlucoseEvent.TYPE_METER)
        events = events.filter(
            or_(
                Event.tags == None,
                Event.tags == '',
                not_(Event.tags.like(r'%Manual%'))
            )
        )
        if self.start:
            events = events.filter(Event.time >= "{}".format(self.start))
        if self.end:
            events = events.filter(Event.time <= "{}".format(self.end))
        events = events.order_by(Event.time)
        data = DataSet(
            events,
            lambda e: e.time.date()
        )

        with open(output, 'wb') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['date', 'time', 'source', 'value', 'unit', 'tags'])
            for (day, daily_log) in data.group.items():
                for event in daily_log:
                        writer.writerow([
                            event.time.strftime('%Y-%m-%d'),
                            event.time.strftime('%I:%M:%S %p'),
                            SOURCE_NAME[event.source],
                            event.value,
                            event.unit,
                            event.tags,
                        ])
