# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import time, timedelta

import numpy
from plotly.graph_objs import Scatter
from plotly.offline import plot

from health_stats.database import DBSession
from health_stats.dataset import DataSet
from health_stats.models.events import *
from ..report import Report



class MeanGlucose(Report):

    def render(self, output):
        # Plot glucose values
        gx = []
        gy = []
        cgx = []
        cgy = []
        gtext = []
        # Plot glucose averages
        ax = []
        ay = []
        atext = []
        ay_upper = []
        ay_lower = []

        session = DBSession()
        events = session.query(GlucoseEvent)
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

            glucose_readings = []
            for event in daily_log:
                glucose_readings.append(int(event.value))
                if event.subtype == GlucoseEvent.TYPE_METER:
                    gx.append(event.time)
                    gy.append(int(event.value))
                    gtext.append("{0}: {1}".format(
                        event.time.strftime('%I:%M %p'), event.value
                    ))
                elif event.subtype == GlucoseEvent.TYPE_CGM:
                    cgx.append(event.time)
                    cgy.append(int(event.value))


            # Process other daily stats
            if glucose_readings:
                avg = '{0:.0f}'.format(numpy.mean(glucose_readings))
                std = '{0:.0f}'.format(numpy.std(glucose_readings))
                # Add the entry
                ax.append(datetime.combine(day, time(12, 0, 0, 0)))
                ay.append(avg)
                ay_upper.append(float(avg) + float(std))
                ay_lower.append(float(avg) - float(std))
                # ay_error.append(std)
                # date_str = daily_log.date.strftime('%b %d')
                # atext.append('{0}: {1} mg/dL avg &plusmn; {2}'.format(date_str, avg, std))
                atext.append(
                    '<b>{}</b><br>{}σ{}'.format(avg, len(glucose_readings), std))

        # Extend the average-reading standard deviation lines to the
        # beginning/end of the graph
        first_date = datetime.combine(min(gx[0], ax[0]).date(), time.min)
        last_date = datetime.combine(max(gx[-1], ax[-1]).date(), time.max)
        ax_std = [first_date, ] + ax + [last_date, ]
        ay_upper.insert(0, ay_upper[0])
        ay_upper.append(ay_upper[-1])
        ay_lower.insert(0, ay_lower[0])
        ay_lower.append(ay_lower[-1])

        plot(
            {
                'data': [
                    # Daily average, standard deviations
                    Scatter(
                        name="daily average",
                        x=ax_std, y=ay_upper,
                        hoverinfo='none',
                        opacity=.3,
                        line={
                            'color': 'transparent',
                            'shape': 'spline'
                        },
                        showlegend=False,
                        mode='lines',
                    ),
                    Scatter(
                        name="daily average",
                        x=ax_std, y=ay_lower,
                        hoverinfo='none',
                        opacity=.3,
                        mode='lines',
                        line={
                            'color': 'transparent',
                            'shape': 'spline'
                        },
                        fillcolor='#A6F4A5',
                        showlegend=False,
                        fill='tonexty'
                    ),
                    # Individual readings
                    Scatter(
                        name="glucose",
                        x=gx, y=gy,
                        text=gtext,
                        hoverinfo='text',
                        mode='lines',
                        line=dict(color='#213ECF'),
                        opacity=.3,
                    ),
                    # Need a better scale before we can show CGM data properly.
                    Scatter(
                        name="cgm",
                        x=cgx, y=cgy,
                        mode='lines+markers',
                        marker={
                            'color': '#008000',
                            'size': 2,
                        },
                        line={
                            'color': '#008000',
                            'shape': 'spline',
                            # 'smoothing': .5,
                        },
                        opacity=.3,
                    ),
                    # Daily average and text labels
                    Scatter(
                        name="daily average",
                        x=ax, y=ay,
                        mode='markers+text',
                        marker={
                            'color': "rgb(16, 180, 60)",
                            'size': 22,
                        },
                        text=atext,
                        hoverinfo='none',
                        textfont={
                            'color': 'white',
                            'size': 6,
                        }
                        # opacity=.8,
                    ),
                ],
                'layout': {
                    'xaxis': {
                        'title': 'Date',
                        'range': [max(gx) - timedelta(days=14), max(gx) + timedelta(hours=1)],
                    },
                    'yaxis': {
                        'title': 'Glucose mg/dL'
                    },
                    'showlegend': False,
                },
            },
            auto_open=False,
            filename=output
        )
