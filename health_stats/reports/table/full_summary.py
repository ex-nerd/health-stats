
# Python 2 and 3
from __future__ import print_function

import csv

from ..report import Report


class FullSummary(Report):

    def render(self, output):
        with open(output, 'wb') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['date', 'time', 'glucose mg/dl', 'insulin:food', 'insulin:correction', 'insulin:basal', 'food:carbs'])
            for event in self.stats.log.events:
                if event.glucose or event.insulin or event.meal.carbs:
                    writer.writerow([
                        event.event_time.strftime('%Y-%m-%d'),
                        event.event_time.strftime('%I:%M:%S %p'),
                        event.glucose,
                        event.insulin.food,
                        event.insulin.correction,
                        event.insulin.basal,
                        event.meal.carbs,
                    ])
