# from builtins import super

import re
import csv
from datetime import datetime

from health_stats import LogEvent, InsulinData, MealData
from health_stats.date_range import DateRange

class LogParser(object):
    """ Abstract top level class for all parsers """

    __slots__ = (
        'date_range',
    )

    def __init__(self, date_range):
        self.date_range = date_range

    def parse_log(self, path):
        """
        Parse the specified path and return a list of LogEvent objects
        Child classes MUST override this method
        """
        raise NotImplementedError('This method must be overridden by a child class')


class CSVLogParser(LogParser):
    """ Abstract parent class for all CSV parsers """

    def parse_log(self, path):
        events = []
        with open(path, 'rb') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                event = self.parse_row(row)
                if event in self.date_range:
                    events.append(event)
        return events

    def parse_row(self, row):
        """
        Parse the values in a CSV row and return a LogEvent
        Child classes MUST override this method
        """
        raise NotImplementedError('This method must be overridden by a child class')


class MySugrLogParser(CSVLogParser):

    # Constants for the column names from mysugr
    LOG_DATE = "Date"
    LOG_TIME = "Time"
    TAGS = "Tags"
    GLUCOSE = "Blood Glucose Measurement (mg/dl)"
    # "Insulin Injection Units (Pen)"
    INSULIN_BASAL = "Basal Injection Units"
    # "Insulin Injection Units (pump)"
    INSULIN_MEAL = "Insulin (Meal)"
    INSULIN_CORRECTION = "Insulin (Correction)"
    # "Temporary Basal Percentage"
    # "Temporary Basal Duration (Minutes)"
    MEAL_CARBS = "Meal Carbohydrates (Grams, Factor 1)"
    MEAL_DESCRIPTION = "Meal Descriptions"
    ACTIVITY_DURATION = "Activity Duration (Minutes)"
    ACTIVITY_INTENSITY = "Activity Intensity (1: Cosy, 2: Ordinary, 3: Demanding)"
    ACTIVITY_DESCRIPTION = "Activity Description"
    STEPS = "Steps"
    NOTE = "Note"
    LOCATION = "Location"
    BLOOD_PRESSURE = "Blood pressure"
    BODY_WEIGHT = "Body weight (lbs)"
    HBA1C = "HbA1c (Percent)"
    KETONES = "Ketones"
    FOOD_TYPE = "Food type"
    MEDICATION = "Medication"

    def parse_row(self, row):

        tags = row[self.TAGS].strip()
        tags = re.split(r'\s*,\s*', tags) if tags else []

        bp = row[self.BLOOD_PRESSURE].strip()
        if bp:
            bp_systolic, bp_diastolic = [int(x) for x in bp.split('/')]
        else:
            bp_systolic, bp_diastolic = None, None

        # @todo use pytz to convert date to utc...

        return LogEvent(
            event_time=datetime.strptime(
                '{0} {1}'.format(row[self.LOG_DATE], row[self.LOG_TIME]),
                '%b %d, %Y %I:%M:%S %p'
            ),
            glucose=int(row[self.GLUCOSE]) if row[self.GLUCOSE] else None,
            insulin=InsulinData(
                basal=(int(row[self.INSULIN_BASAL]) if row[self.INSULIN_BASAL] else None),
                meal=(int(row[self.INSULIN_MEAL]) if row[self.INSULIN_MEAL] else None),
                correction=(int(row[self.INSULIN_CORRECTION]) if row[self.INSULIN_CORRECTION] else None),
            ),
            meal=MealData(
                carbs=(float(row[self.MEAL_CARBS]) if row[self.MEAL_CARBS] else None),
                description=(row[self.MEAL_DESCRIPTION].strip() or None),
            ),
            note=row[self.NOTE].strip() or None,
            location=row[self.LOCATION].strip() or None,
            tags=tags,
            bp_systolic=bp_systolic,
            bp_diastolic=bp_diastolic,
            weight_lbs=float(row[self.BODY_WEIGHT]) if row[self.BODY_WEIGHT] else None,
        )

Parsers = {
    'mysugr_csv': MySugrLogParser,
}
