# -*- coding: utf-8 -*-

from health_stats.models.events import *
from datetime import datetime
from . import CSVLogParser


class DexcomClarityLogParser(CSVLogParser):

    SOURCE = SOURCE_DEXCOM_CLARITY

    # Constants for the column names from dexcom
    INDEX = "Index"
    TIMESTAMP = "Timestamp (YYYY-MM-DDThh:mm:ss)"
    EVENT_TYPE = "Event Type"
    EVENT_SUBTYPE = "Event Subtype"
    PATIENT_INFO = "Patient Info"
    DEVICE_INFO = "Device Info"
    SOURCE_DEVICE_ID = "Source Device ID"
    GLUCOSE_VALUE = "Glucose Value (mg/dL)"
    INSULIN_VALUE = "Insulin Value (u)"
    CARB_VALUE = "Carb Value (grams)"
    DURATION = "Duration (hh:mm:ss)"
    GLUCOSE_RATE_OF_CHANGE = "Glucose Rate of Change (mg/dL/min)"
    TRANSMITTER_TIME = "Transmitter Time (Long Integer)"

    # Entry types
    TYPE_INSULIN = "Insulin"
    TYPE_CARBS = "Carbs"
    TYPE_GLUCOSE = "EGV"
    TYPE_CALIBRATION = "Calibration"

    def parse_row(self, row):
        # User-info rows don't have a timestamp and should just be skipped
        if not row[self.TIMESTAMP]:
            return

        event_time = datetime.strptime(
            row[self.TIMESTAMP],
            '%Y-%m-%dT%H:%M:%S'
        )

        if row[self.EVENT_TYPE] == self.TYPE_GLUCOSE:
            value = int(row[self.GLUCOSE_VALUE]) if row[self.GLUCOSE_VALUE] else 0
            if not value:
                return None
            return GlucoseEvent(
                source=self.SOURCE,
                subtype=GlucoseEvent.TYPE_CGM,
                time=event_time,
                value=value,
                unit=GlucoseEvent.UNIT_MGDL,  # Dexcom hard-codes to mg/dL
                notes=None,
                tags='Manual',  # All dexcom glucose events are manual
            )
        # elif row[self.EVENT_TYPE] == self.TYPE_INSULIN:
        #     # TODO: Re-enable if we don't get it from another richer data source
        #     value = int(row[self.INSULIN_VALUE]) if row[self.INSULIN_VALUE] else 0
        #     return InsulinEvent(
        #         source=self.SOURCE,
        #         time=event_time,
        #         subtype=None,  # Dexcom doesn't differentiate between insulin types
        #         value=value,
        #         notes=None,
        #     )
        # elif row[self.EVENT_TYPE] == self.TYPE_CARBS:
        #     # TODO: Re-enable if we don't get it from another richer data source
        #     value = int(row[self.CARB_VALUE]) if row[self.CARB_VALUE] else 0
        #     return CarbsEvent(
        #         source=self.SOURCE,
        #         time=event_time,
        #         value=value,
        #         unit='g',  # Dexcom hard-codes to g
        #         notes=None,
        #     )
        #
