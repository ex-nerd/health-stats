
from datetime import datetime, time, timedelta

from plotly.offline import plot
from plotly.graph_objs import Bar, Scatter

from ..report import Report

from health_stats.models.events import *
from health_stats.database import DBSession
from health_stats.dataset import DataSet


class DailyInsulin(Report):

    def render(self, output):
        # Plot insulin values
        long_x = []
        long_y = []
        rapid_x = []
        rapid_y = []
        day_x = []
        day_y = []

        started = False

        session = DBSession()
        events = session.query(InsulinEvent)
        if self.start:
            events = events.filter(Event.time >= "{}".format(self.start))
        if self.end:
            events = events.filter(Event.time <= "{}".format(self.end))
        events = events.order_by(Event.time)
        data = DataSet(
            events,
            lambda e: e.time.date()
        )

        for (day, daily_log) in data.group.items():

            rapid_insulin = []
            long_insulin = []

            for event in daily_log:
                started = True
                if event.subtype == InsulinEvent.TYPE_LONG:
                    long_insulin.append(int(event.value))
                elif event.subtype == InsulinEvent.TYPE_RAPID:
                    rapid_insulin.append(int(event.value))
                elif event.subtype is None or event.subtype == InsulinEvent.TYPE_OTHER:
                    # @todo make an "other insulin" variable
                    rapid_insulin.append(int(event.value))
                else:
                    raise Exception("Undefined InsulinEvent subtype: {}".format(event.subtype))

            # don't start counting days until we get at least one data point
            if not started:
                continue

            long_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            rapid_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            day_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            long_y.append(sum(long_insulin) if long_insulin else None)
            rapid_y.append(sum(rapid_insulin) if rapid_insulin else None)

            day_total = 0
            if long_y[-1]:
                day_total += long_y[-1]
            if rapid_y[-1]:
                day_total += rapid_y[-1]

            day_y.append(day_total if day_total else None)

        # Restrict the viewport
        min_x = max(day_x) - timedelta(days=14)
        max_x = max(day_x) + timedelta(days=1)

        plot(
            {
                'data': [
                    Bar(
                        name="Long",
                        x=long_x, y=long_y,
                    ),
                    Bar(
                        name="Rapid",
                        x=rapid_x, y=rapid_y,
                    ),
                    Scatter(
                        name="Total",
                        x=day_x, y=( [None] * len(day_y)),
                        # x=day_x, y=day_y,
                        text=day_y,
                        mode='markers+text',
                        # mode='none',
                        marker={
                            'size': 30,
                        },
                        textfont={
                            'color': 'white',
                        },
                        # hoverinfo='none',
                        hoverinfo='markers+text',
                        showlegend=False,
                    ),
                ],
                'layout': {
                    'xaxis': {
                        'title': 'Date',
                        'range': [min_x, max_x],
                    },
                    'yaxis': {'title': 'Insulin (u)'},
                    #'barmode': 'stack',
                    'barmode': 'group',
                },
            },
            auto_open=False,
            filename=output
        )
