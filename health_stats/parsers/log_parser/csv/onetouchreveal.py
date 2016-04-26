from datetime import datetime
from pretty import pprint

from . import CSVLogParser

from health_stats.models.events import *


class OneTouchRevealLogParser(CSVLogParser):

    # FIRST_LINE = 'Item Type,Date and Time,Value,Unit,Manual,Additional Value,Notes'

    # Constants for the column names from mysugr
    ITEM_TYPE = "Item Type"
    DATE_TIME = "Date and Time"
    VALUE = "Value"
    UNIT = "Unit"
    MANUAL = "Manual"
    ADDITIONAL_VALUE = "Additional Value"
    NOTES = "Notes"

    # Entry types
    TYPE_INSULIN = "Insulin"
    TYPE_CARBS = "Carbs"
    TYPE_GLUCOSE = "Blood Sugar Reading"
    TYPE_ACTIVITY = "Activity"

    # Types of insulin
    INSULIN_LONG = "Long"
    INSULIN_RAPID = "Rapid"

    # Types of activity
    ACTIVITY_LIGHT = "Light"
    ACTIVITY_MODERATE = "Moderate"
    ACTIVITY_INTENSE = "Intense"

    def parse_row(self, row):

        # @todo use pytz to convert date to utc...
        event_time = datetime.strptime(
            row[self.DATE_TIME],
            '%m/%d/%y, %I:%M %p'
        )

        if row[self.ITEM_TYPE] == self.TYPE_INSULIN:

            if row[self.UNIT] != 'u':
                raise ValueError("Unrecognized unit in row {}".format(', '.join(row)))

            if row[self.ADDITIONAL_VALUE] == self.INSULIN_LONG:
                insulin_type = InsulinEvent.TYPE_LONG
            elif row[self.ADDITIONAL_VALUE] == self.INSULIN_RAPID:
                insulin_type = InsulinEvent.TYPE_RAPID
            else:
                # @todo support other insulin types
                insulin_type = None

            return InsulinEvent(
                time=event_time,
                subtype=insulin_type,
                value=int(row[self.VALUE]),
                notes=(row[self.NOTES].strip() or None),
            )

        elif row[self.ITEM_TYPE] == self.TYPE_CARBS:

            if row[self.UNIT] != 'g':
                raise ValueError("Unrecognized unit in row {}".format(', '.join(row)))

            return CarbsEvent(
                time=event_time,
                value=(float(row[self.VALUE]) if row[self.VALUE] else 0),
                unit='g',
                notes=(row[self.NOTES].strip() or None),
            )

        elif row[self.ITEM_TYPE] == self.TYPE_GLUCOSE:

            if row[self.UNIT] != 'mg/dL':
                raise ValueError("Unrecognized unit in row {}".format(', '.join(row)))
            if row[self.MANUAL] == 'Yes':
                if row[self.ADDITIONAL_VALUE]:
                    row[self.ADDITIONAL_VALUE] += ', '
                row[self.ADDITIONAL_VALUE] += 'Manual'
            elif row[self.MANUAL] != 'No':
                raise ValueError("Unrecognized 'manual' in row {}".format(', '.join(row)))

            return GlucoseEvent(
                time=event_time,
                value=int(row[self.VALUE]) if row[self.VALUE] else 0,
                unit=GlucoseEvent.UNIT_MGDL,
                notes=(row[self.NOTES].strip() or None),
                tags=(row[self.ADDITIONAL_VALUE].strip() or None),
            )
