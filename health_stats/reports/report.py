
class Report(object):
    """ Parent class for all reports """

    __slots__ = ('stats')

    def __init__(self, stats):
        self.stats = stats

    def render(self, output):
        """ Render the report to the specified output file """
        raise NotImplementedError("This abstract method must be implemented by the child class.")
