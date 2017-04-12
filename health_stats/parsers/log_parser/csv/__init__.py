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

        # find earlieriest/latest and delete any existing rows from this range
        reader = unicode_csv_dictreader(path)
        firstrow = reader.next()
        for lastrow in reader:
            pass
        # @todo time isn't getting validated yet here.....
        t1 = self.parse_row(firstrow).time
        t2 = self.parse_row(lastrow).time
        if t1 > t2:
            t1, t2 = t2, t1
        # To avoid false duplicates and clear out any data altered/removed in
        # the source, delete any existing rows from this source and time period.
        num = session.query(Event) \
            .filter(Event.time >= "{}.000000".format(t1)) \
            .filter(Event.time <= "{}.000000".format(t2)) \
            .filter(Event.source == "{}".format(self.SOURCE)) \
            .delete()
        print("Deleting {} events from this source between {} and {}".format(num, t1, t2))
        session.commit()
        # sys.exit()

        # Now we can restart the csv reader to actually load the data
        reader = unicode_csv_dictreader(path)
        num = 0
        for row in reader:
            session.merge(self.parse_row(row))
            num += 1
        print("Adding {} events".format(num))
        session.commit()

    def parse_row(self, row):
        """
        Parse the values in a CSV row and return a LogEvent
        Child classes MUST override this method
        """
        raise NotImplementedError('This method must be overridden by a child class')
