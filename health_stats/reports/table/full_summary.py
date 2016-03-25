
# Python 2 and 3
from __future__ import print_function

import csv

from ..report import Report


class FullSummary(Report):

    def render(self, output):
        with open(output, 'wb') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['date', 'time', 'glucose mg/dl'])
            for event in self.stats.log.events:
                if not event.glucose:
                    continue
                writer.writerow([event.event_time.strftime('%Y-%m-%d'), event.event_time.strftime('%I:%M:%S %p'), event.glucose])
