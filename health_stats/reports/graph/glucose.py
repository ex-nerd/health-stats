
from datetime import datetime, time

from plotly.offline import plot
from plotly.graph_objs import Scatter


def mean_glucose(stats, output):
    # Plot glucose values
    gx = []
    gy = []
    gtext = []
    # Plot glucose averages
    ax = []
    ay = []
    atext = []
    ay_error = []
    ay_upper = []
    ay_lower = []

    for (day, daily_log) in stats.days.items():

        glucose_readings = 0
        for event in daily_log.events:
            text_log = []
            if event.glucose:
                glucose_readings += 1
                gx.append(event.event_time)
                gy.append(event.glucose)
                text_log.append('glucose:   {0} mg/dl'.format(event.glucose))
            if event.insulin.basal:
                text_log.append('lantus:    {0}'.format(event.insulin.basal))
            if event.meal.carbs:
                text_log.append('carbs:     {0}g'.format(event.meal.carbs))
            if event.meal.description:
                text_log.append('meal:      {0}'.format(event.meal.description))
            if len(event.tags):
                text_log.append('tags:      {0}'.format(', '.join(event.tags)))
            # We have to added the gtext after collecting all of the other data points
            if event.glucose:
                gtext.append("{0}:<br>\n    {1}".format(event.event_time.strftime('%I:%M %p'), '<br>\n    '.join(text_log)))

        # Process other daily stats
        avg = daily_log.glucose_mean()
        if avg is not None:
            std = daily_log.glucose_std()
            # Add the entry
            ax.append(datetime.combine(day, time(12, 0, 0, 0)))
            ay.append(avg)
            ay_upper.append(float(avg) + float(std))
            ay_lower.append(float(avg) - float(std))
            # ay_error.append(std)
            # date_str = daily_log.date.strftime('%b %d')
            # atext.append('{0}: {1} mg/dl avg &plusmn; {2}'.format(date_str, avg, std))
            atext.append('<b>{}</b><br>{}&sigma;{}'.format(avg, glucose_readings, std))

    # Extend the average-reading standard deviation lines to the beginning/end of the graph
    first_date = datetime.combine(min(gx[0], ax[0]).date(), time.min)
    last_date = datetime.combine(max(gx[-1], ax[-1]).date(), time.max)
    ax_std = [first_date, ] + ax + [last_date, ]
    ay_upper.insert(0, ay_upper[0])
    ay_upper.append(ay_upper[-1])
    ay_lower.insert(0, ay_lower[0])
    ay_lower.append(ay_lower[-1])

    # Render the graph
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
                # Daily average and text labels
                Scatter(
                    name="daily average",
                    x=ax, y=ay,
                    # error_y={
                    #     'type': 'data',
                    #     'array': ay_error,
                    #     'opacity': .8,
                    #     'color': "rgb(16, 180, 60)",
                    #     'visible': False,
                    # },
                    mode='markers+text',
                    marker={
                        'color': "rgb(16, 180, 60)",
                        'size': 50,
                    },
                    text=atext,
                    hoverinfo='none',
                    textfont={
                        'color': 'white',
                    }
                    # opacity=.8,
                ),
            ],
            'layout': {
                'xaxis': {'title': 'Date'},
                'yaxis': {'title': 'Glucose mg/dl'},
                'showlegend': False,
            },
        },
        auto_open=False,
        filename=output
    )
