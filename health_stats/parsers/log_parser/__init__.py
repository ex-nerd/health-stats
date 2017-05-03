# -*- coding: utf-8 -*-

from health_stats.models.events import Event


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

    @staticmethod
    def _flush_old_data(session, event_source, min_time, max_time):
        # To avoid false duplicates and clear out any data altered/removed in
        # the source, delete any existing rows from this source and time period.
        num = session.query(Event) \
            .filter(Event.time >= "{}.000000".format(min_time)) \
            .filter(Event.time <= "{}.000000".format(max_time)) \
            .filter(Event.source == "{}".format(event_source)) \
            .delete()
        print("Deleting {} {} events between {} and {}".format(num, event_source, min_time, max_time))
        session.commit()
