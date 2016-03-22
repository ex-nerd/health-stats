
# Python 2 and 3
from __future__ import print_function

from collections import OrderedDict


def glucose_summary(stats, output):

    with open(output, 'wb') as txt_file:
        for (day, daily_log) in reversed(stats.days.items()):
            print(day.strftime('%b %d, %Y') + "\n", file=txt_file)
            for event in reversed(daily_log.events):
                text_log = []
                if event.glucose:
                    text_log.append('glucose:   {0} mg/dl'.format(event.glucose))
                if event.insulin.basal:
                    text_log.append('lantus:    {0}'.format(event.insulin.basal))
                # if row[MEDICATION]:
                #    format:  medication_name (1.000000)
                #    Not sure what this looks like with multiple medications per event
                if event.meal.carbs:
                    text_log.append('carbs:     {0}g'.format(event.meal.carbs))
                if event.meal.description:
                    text_log.append('meal:      {0}'.format(event.meal.description))
                if event.note:
                    text_log.append('note:      {0}'.format(event.note))
                if len(event.tags):
                    text_log.append('tags:      {0}'.format(', '.join(event.tags)))
            # Write out any daily events to the text log
                if text_log:
                    print("{0}:\n    {1}\n".format(event.event_time.strftime('%I:%M %p'), '\n    '.join(text_log)), file=txt_file)
            print(file=txt_file)
