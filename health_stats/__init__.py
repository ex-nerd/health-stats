"""
health-stats
====
"""

# from pretty import pprint

__version__ = '0.0.1'


# class HealthStats(object):

#     __slots__ = (
#         'log',
#         'days',
#     )

#     def __init__(self):
#         self.log = EventLog()
#         self.days = OrderedDict()

#     def extend(self, events):
#         self.log.extend(events)

#     def load_from_db(self, query):
#         self.log = EventLog()
#         self.extend(query.all())
#         self.populate_days()

#     def analyze(self):
#         self.log.sort()
#         self.populate_days()

#     def populate_days(self):
#         self.days = OrderedDict()
#         for event in self.log.events:
#             # Add this event to the group-by-days entries
#             day = event.time.date()
#             if day not in self.days:
#                 self.days[day] = EventLog()
#             self.days[day].add(event)
#             # @todo group by other time periods?

#     def __pretty__(self, p, cycle):
#         p.text('<{0}: '.format(type(self).__name__))
#         if cycle:
#             p.text('...')
#         else:
#             p.pretty({
#                 'log': self.log,
#                 'days': self.days.keys(),
#             })
#         p.text('>')


# class EventLog(object):

#     __slots__ = ('events')

#     def __init__(self):
#         self.events = []

#     def sort(self):
#         self.events.sort()

#     def add(self, event):
#         self.events.append(event)

#     def extend(self, events):
#         self.events.extend(events)

#     def glucose_values(self):
#         values = []
#         for event in self.events:
#             if isinstance(event, GlucoseEvent):
#                 values.append(event.value)
#         return values

#     def glucose_mean(self):
#         values = self.glucose_values()
#         if len(values) > 0:
#             return '{0:.0f}'.format(numpy.mean(values))
#         return None

#     def glucose_std(self):
#         values = self.glucose_values()
#         if len(values) > 0:
#             return '{0:.0f}'.format(numpy.std(values))
#         return None

#     def carb_values(self):
#         values = []
#         for event in self.events:
#             if isinstance(event, CarbsEvent):
#                 values.append(event.value)
#         return values

#     def __pretty__(self, p, cycle):
#         p.text('<{0}: '.format(type(self).__name__))
#         if cycle:
#             pass
#         else:
#             p.pretty({
#                 'events': self.events,
#             })
#         p.text('>')

