
from collections import OrderedDict

class DataSet(object):

    __slots__ = (
        'events',  # List of all events in this data set
        'group',   # Iterable containing groups of events
    )

    def __init__(self, query, group_function):
        self.events = query.all()
        if group_function is None:
            self.group = self.events
        elif callable(group_function):
            self.group = OrderedDict()
            for event in self.events:
                # Add this event to the group-by entries
                key = group_function(event)
                if key not in self.group:
                    self.group[key] = []
                self.group[key].append(event)
        else:
            raise ValueError("group_function is not callable")

    def __pretty__(self, p, cycle):
        p.text('<{0}: '.format(type(self).__name__))
        if cycle:
            p.text('...')
        else:
            p.pretty({
                'events': self.events,
                'group': self.group.keys(),
            })
        p.text('>')
