
import re
from datetime import datetime

from . import CSVLogParser

from health_stats.models.events import *

class MySugrLogParser(CSVLogParser):

    # Constants for the column names from mysugr
    LOG_DATE = "Date"
    LOG_TIME = "Time"
    TAGS = "Tags"
    GLUCOSE = "Blood Glucose Measurement (mg/dL)"
    INSULIN_UNITS_PEN = "Insulin Injection Units (Pen)"
    INSULIN_BASAL = "Basal Injection Units"
    INSULIN_UNITS_PUMP = "Insulin Injection Units (pump)"
    INSULIN_MEAL = "Insulin (Meal)"
    INSULIN_CORRECTION = "Insulin (Correction)"
    TEMP_BASAL_PERCENTAGE = "Temporary Basal Percentage"
    TEMP_BASAL_DURATION = "Temporary Basal Duration (Minutes)"
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

        raise NotImplementedError("Needs to be updated for sqlalchemy")

        tags = row[self.TAGS].strip()
        tags = re.split(r'\s*,\s*', tags) if tags else []

        bp = row[self.BLOOD_PRESSURE].strip()
        if bp:
            bp_systolic, bp_diastolic = [int(x) for x in bp.split('/')]
        else:
            bp_systolic, bp_diastolic = None, None

        # @todo use pytz to convert date to utc...

        return Event(
            event_time=datetime.strptime(
                '{0} {1}'.format(row[self.LOG_DATE], row[self.LOG_TIME]),
                '%b %d, %Y %I:%M:%S %p'
            ),
            glucose=int(row[self.GLUCOSE]) if row[self.GLUCOSE] else None,
            insulin=InsulinData(
                basal=(int(row[self.INSULIN_BASAL]) if row[self.INSULIN_BASAL] else None),
                food=(int(row[self.INSULIN_MEAL]) if row[self.INSULIN_MEAL] else None),
                correction=(int(row[self.INSULIN_CORRECTION]) if row[self.INSULIN_CORRECTION] else None),
            ),
            meal=FoodData(
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
