import csv

from .. import LogParser

import csv
import codecs

from health_stats.database import DBSession

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
        reader = unicode_csv_dictreader(path)
        for row in reader:
            session.merge(self.parse_row(row))
        session.commit()

    def parse_row(self, row):
        """
        Parse the values in a CSV row and return a LogEvent
        Child classes MUST override this method
        """
        raise NotImplementedError('This method must be overridden by a child class')
