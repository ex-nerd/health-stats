
from datetime import datetime, time

from plotly.offline import plot
from plotly.graph_objs import Bar, Scatter

from ..report import Report


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

        for (day, daily_log) in self.stats.days.items():

            morn_carbs = []
            noon_carbs = []
            eve_carbs = []

            for event in daily_log.events:
                if not event.meal:
                    continue
                started = True
                hour = event.event_time.hour
                minute = event.event_time.minute
                if hour >= 17 or hour <= 4:
                    eve_carbs.append(event.meal.carbs)
                elif hour > 11 or (hour == 11 and minute >= 15):
                    noon_carbs.append(event.meal.carbs)
                else:
                    morn_carbs.append(event.meal.carbs)

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
                            'size': 30,
                        },
                        textfont={
                            'color': 'white',
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
