
class Report(object):
    """ Parent class for all reports """

    __slots__ = (
        'stats',
        'start',
        'end',
    )

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def render(self, output):
        """ Render the report to the specified output file """
        raise NotImplementedError("This abstract method must be implemented by the child class.")

    def load_events(self):
        return []
