
# Python 2 and 3
from __future__ import print_function

from ..report import Report

from health_stats.models.events import *
from health_stats.database import DBSession
from health_stats.dataset import DataSet

class DailySummary(Report):

    def render(self, output):

        session = DBSession()
        events = session.query(Event)
        if self.start:
            events = events.filter(Event.time >= "{}".format(self.start))
        if self.end:
            events = events.filter(Event.time <= "{}".format(self.end))
        events = events.order_by(Event.time)
        data = DataSet(
            events,
            lambda e: e.time.date()
        )

        with open(output, 'wb') as txt_file:
            for (day, daily_log) in reversed(data.group.items()):
                print(day.strftime('%b %d, %Y') + "\n", file=txt_file)
                for event in reversed(daily_log):
                    text_log = []
                    if event.type == TYPE_GLUCOSE:
                        text_log.append('glucose:   {0} mg/dl'.format(event.value))
                    if event.type == TYPE_INSULIN:
                        if event.subtype == InsulinEvent.TYPE_LONG:
                            text_log.append('lantus:    {0}'.format(event.value))
                        if event.subtype == InsulinEvent.TYPE_RAPID:
                            text_log.append('humalog:   {0}'.format(event.value))
                    if event.type == TYPE_CARBS:
                        text_log.append('carbs:     {0}g'.format(event.value))
                    if event.notes:
                        text_log.append('note:      {0}'.format(event.notes))
                    if event.tags:
                        text_log.append('tags:      {0}'.format(event.tags))
                # Write out any daily events to the text log
                    if text_log:
                        print("{0}:\n    {1}\n".format(event.time.strftime('%I:%M %p'), '\n    '.join(text_log)), file=txt_file)
                print(file=txt_file)
