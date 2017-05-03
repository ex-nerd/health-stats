# -*- coding: utf-8 -*-

from zipfile import ZipFile

import dateparser
from lxml import etree

from health_stats.database import DBSession
from health_stats.models.events import *
from health_stats.parsers.log_parser import LogParser


# Healthkit constants we care about
# See: https://developer.apple.com/library/watchos/documentation/HealthKit/Reference/HealthKit_Constants/index.html
TYPE_GLUCOSE = "HKQuantityTypeIdentifierBloodGlucose"
TYPE_BP_DIASTOLIC = "HKQuantityTypeIdentifierBloodPressureDiastolic"
TYPE_BP_SYSTOLIC = "HKQuantityTypeIdentifierBloodPressureSystolic"
TYPE_CARBS = "HKQuantityTypeIdentifierDietaryCarbohydrates"
TYPE_DISTANCE_WALKING_RUNNING = "HKQuantityTypeIdentifierDistanceWalkingRunning"
TYPE_FLIGHTS_CLIMBED = "HKQuantityTypeIdentifierFlightsClimbed"
TYPE_STEP_COUNT = "HKQuantityTypeIdentifierStepCount"


class HealthkitLogParser(LogParser):
    """ Parser for Apple Healthkit data """

    SOURCE = SOURCE_APPLE_HEALTH

    def parse_log(self, path):
        session = DBSession()

        # This file is big enough (and compressed) that we might as well just parse
        # it once and worry about saving memory if/when that becomes an issue.
        hk_events = []
        with ZipFile(path, 'r') as zfile:
            xfile = zfile.open('apple_health_export/export.xml')
            tree = etree.parse(xfile)
            root = tree.getroot()
            for rnum, record in enumerate(root.iterfind('.//Record'), start=1):
                event = self.parse_record(record)
                if event:
                    hk_events.append(event)

        # find earliest/latest and delete any existing rows from this range
        times = [e.time for e in hk_events]
        self._flush_old_data(session, self.SOURCE, min(times), max(times))
        session.commit()

        # Now we can restart the csv reader to actually load the data
        for event in hk_events:
            session.merge(event)
        print("Adding {} events".format(len(hk_events)))
        session.commit()

    def parse_record(self, record):
        """
        Parse the values in an xml record and return a LogEvent
        """
        # Determine if we want this record
        source_name = record.attrib['sourceName']
        # source_version = record.attrib.get('sourceVersion')
        # todo: We will probably need special handline for sourceName values that we know about from other importers.
        # todo: e.g. OneTouch should be converted into OneTouch source events (or ignored, since csv data is richer).
        # Parse out other basics about the record
        record_type = record.attrib['type']
        unit = record.attrib['unit']
        value = record.attrib['value']
        # Parse the dates and pick the most appropriate one.
        # Note: too many other formats are always in "local time", so don't bother trying to deal with tz for now.
        event_time = datetime.strptime(record.attrib['endDate'][:19], '%Y-%m-%d %H:%M:%S')
        if not event_time:
            event_time = datetime.strptime(record.attrib['startDate'][:19], '%Y-%m-%d %H:%M:%S')
        if not event_time:
            event_time = datetime.strptime(record.attrib['creationDate'][:19], '%Y-%m-%d %H:%M:%S')
        # Find the wanted metadata fields
        metadata = {}
        for meta in record.iterfind('.//MetadataEntry'):
            metadata[meta.attrib['key']] = meta.attrib['value']
        # Deal with various record types
        # if record_type == TYPE_GLUCOSE:
        # TODO: re-enable this once we can exclude sources we already get from elsewhere
        #     if unit != 'mg/dL':
        #         raise ValueError("Unrecognized unit in record {}".format(', '.join(record)))
        #     tags = []
        #     if int(metadata.get('HKWasUserEntered', 0)) == 1:
        #         tags.append('Manual')
        #     if metadata.get('Tag Type', 'None') != 'None':  # yes, it's stored as the string 'None'
        #         tags.append(metadata['Tag Type'])
        #     return GlucoseEvent(
        #         source=self.SOURCE,
        #         time=event_time,
        #         value=value,
        #         unit=GlucoseEvent.UNIT_MGDL,
        #         notes=None,
        #         tags=', '.join(tags),
        #     )
        # elif record_type == TYPE_BP_DIASTOLIC:
        #     if unit != 'mmHg':
        #         raise ValueError("Unrecognized unit in record {}".format(', '.join(record)))
        #     TODO: Implement this if there are no better sources
        # elif record_type == TYPE_BP_SYSTOLIC:
        #     if unit != 'mmHg':
        #         raise ValueError("Unrecognized unit in record {}".format(', '.join(record)))
        #     TODO: Implement this if there are no better sources
        # elif record_type == TYPE_CARBS:
        #     if unit != 'g':
        #         raise ValueError("Unrecognized unit in record {}".format(', '.join(record)))
        #     TODO: Implement this if there are no better sources
        if record_type == TYPE_STEP_COUNT:
            if value < 1:
                return None
            if unit != 'count':
                raise ValueError("Unrecognized unit in record {}".format(', '.join(record)))
            return StepsEvent(
                source=self.SOURCE,
                time=event_time,
                value=value,
                unit='count',
            )
