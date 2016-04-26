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
