
from datetime import datetime, time

from plotly.offline import plot
from plotly.graph_objs import Bar

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

        for (day, daily_log) in self.stats.days.items():

            morn_carbs = []
            noon_carbs = []
            eve_carbs = []

            for event in daily_log.events:
                if not event.meal:
                    continue
                hour = event.event_time.hour
                minute = event.event_time.minute
                if hour > 17 or hour <= 4:
                    eve_carbs.append(event.meal.carbs)
                elif hour > 11 or (hour == 11 and minute >= 30):
                    noon_carbs.append(event.meal.carbs)
                else:
                    morn_carbs.append(event.meal.carbs)

            morn_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            noon_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            eve_x.append(datetime.combine(day, time(12, 0, 0, 0)))
            morn_y.append(sum(morn_carbs))
            noon_y.append(sum(noon_carbs))
            eve_y.append(sum(eve_carbs))

        plot(
            {
                'data': [
                    Bar(
                        name="Morning",
                        x=morn_x, y=morn_y,
                    ),
                    Bar(
                        name="Afternoon",
                        x=noon_x, y=noon_y,
                    ),
                    Bar(
                        name="Evening",
                        x=eve_x, y=eve_y,
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
