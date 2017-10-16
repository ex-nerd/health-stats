import csv

from .. import LogParser

import csv
import codecs

from health_stats.database import DBSession
from health_stats.models.events import Event

# Dealing with unicode: https://gist.github.com/pkqk/4026444
def unicode_csv_dictreader(path, *args, **kwargs):
    "create a csv dict reader that copes with encoding correctly"
    # utf-8-sig strips off a BOM if it's present
    stream = codecs.open(path, encoding='utf-8-sig')
    return UnicodeCSVDictReader(stream, *args, **kwargs)


class UnicodeCSVDictReader(csv.DictReader):
    def __init__(self, unicode_csvfile, *args, **kwargs):
        decoder = codecs.getdecoder('utf-8')
        self.decoder = lambda v: decoder(v)[0]
        utf8_csvfile = codecs.iterencode(unicode_csvfile, encoding='utf-8')
        # bollicks to csv.DictReader being an oldstyle class
        csv.DictReader.__init__(self, utf8_csvfile, *args, **kwargs)
        self.fieldnames = [self.decoder(f) for f in self.fieldnames]

    def next(self):
        data = csv.DictReader.next(self)
        return {k: self.decoder(v) for (k, v) in data.iteritems()}


class CSVLogParser(LogParser):
    """ Abstract parent class for all CSV parsers """

    def parse_log(self, path):
        session = DBSession()

        # Read in all of the events.
        # Use a dict because we occasionally see duplicate entries, and session.merge() isn't perfect.
        reader = unicode_csv_dictreader(path)
        csv_events = {}
        for row in reader:
            event = self.parse_row(row)
            if event:
                csv_events[event.id] = event

        # find earlieriest/latest and delete any existing rows from this range
        times = [e.time for e in csv_events.values()]
        self._flush_old_data(session, self.SOURCE, min(times), max(times))
        session.commit()

        # Now we can restart the csv reader to actually load the data
        # There are some
        for event in csv_events.values():
            session.merge(event)
        print("Adding {} events".format(len(csv_events)))
        session.commit()

    def parse_row(self, row):
        """
        Parse the values in a CSV row and return a LogEvent
        Child classes MUST override this method
        """
        raise NotImplementedError('This method must be overridden by a child class')
