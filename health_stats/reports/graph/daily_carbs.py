
from datetime import datetime, time

from plotly.offline import plot
from plotly.graph_objs import Bar, Scatter

from ..report import Report

from health_stats.models.events import *
from health_stats.database import DBSession
from health_stats.dataset import DataSet


class DailyCarbs(Report):

    def render(self, output):
        # Plot carb values
        morn_x = []
        morn_y = []
        noon_x = []
        noon_y = []
        eve_x = []
        eve_y = []
        day_x = []
        day_y = []

        started = False

        session = DBSession()
        events = session.query(CarbsEvent)
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

            morn_carbs = []
            noon_carbs = []
            eve_carbs = []

            for event in daily_log:
                started = True
                hour = event.time.hour
                minute = event.time.minute
                if hour >= 17 or hour <= 4:
                    eve_carbs.append(float(event.value))
                elif hour > 11 or (hour == 11 and minute >= 15):
                    noon_carbs.append(float(event.value))
                else:
                    morn_carbs.append(float(event.value))

            # don't start counting days until we get at least one data point
            if not started:
                continue

            morn_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            noon_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            eve_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            day_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            morn_y.append(sum(morn_carbs) if morn_carbs else None)
            noon_y.append(sum(noon_carbs) if noon_carbs else None)
            eve_y.append(sum(eve_carbs) if eve_carbs else None)

            day_total = 0
            if morn_y[-1]:
                day_total += morn_y[-1]
            if noon_y[-1]:
                day_total += noon_y[-1]
            if eve_y[-1]:
                day_total += eve_y[-1]

            day_y.append(day_total if day_total else None)

        plot(
            {
                'data': [
                    Bar(
                        name="Evening",
                        x=eve_x, y=eve_y,
                    ),
                    Bar(
                        name="Afternoon",
                        x=noon_x, y=noon_y,
                    ),
                    Bar(
                        name="Morning",
                        x=morn_x, y=morn_y,
                    ),
                    Scatter(
                        name="Total",
                        x=day_x, y=day_y,
                        text=day_y,
                        mode='markers+text',
                        marker={
                            'size': 16,
                        },
                        textfont={
                            'color': 'white',
                            'size': 6,
                        },
                        hoverinfo='none',
                        showlegend=False,
                    ),
                ],
                'layout': {
                    'xaxis': {'title': 'Date'},
                    'yaxis': {'title': 'Carbs (g)'},
                    'barmode': 'stack',
                },
            },
            auto_open=False,
            filename=output
        )
