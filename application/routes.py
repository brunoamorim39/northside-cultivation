from flask import render_template, jsonify
import json
import pandas as pd
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import csv

from __init__ import app, db
from models import DataLog

@app.route('/', methods=['GET'])
def index():
    # Pulls sample data from database and prepares it for display via Plotly
    sample_data = data_log()
    sample_ids = []
    time_axis = []
    temperature_axis = []
    humidity_axis = []
    co2_axis = []

    for sample_object in sample_data:
        sample_ids.append(sample_object['sample_number'])
        time_axis.append(pd.to_datetime(sample_object['current_time']))
        temperature_axis.append(sample_object['temperature'])
        humidity_axis.append(sample_object['humidity'])
        co2_axis.append(sample_object['co2_content'])

    # Plotly configuration for interactive subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.075,
        subplot_titles=('Temperature', 'Humidity', 'CO2 Content')
        )

    fig.add_trace(go.Scatter(x=time_axis, y=temperature_axis, name='Temperature'),
        row=1, col=1)
        
    fig.add_trace(go.Scatter(x=time_axis, y=humidity_axis, name='Humidity'),
        row=2, col=1)
        
    fig.add_trace(go.Scatter(x=time_axis, y=co2_axis, name='CO2 Content'),
        row=3, col=1)
        
    fig.update_layout(
        height=1200,
        showlegend=False,
        title_text='Fruiting Room Environment Data'
        )

    config = ({
        'scrollZoom': True,
        'displaylogo': False
        })

    fig.show(config=config)
    graph_JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Captures realtime data of the environment to display
    rt_time, rt_temperature, rt_humidity, rt_co2_level = get_realtime()

    return render_template('index.html',
        graph_JSON=graph_JSON,
        rt_time=rt_time,
        rt_temperature=rt_temperature,
        rt_humidity=rt_humidity,
        rt_co2_level=rt_co2_level
        )

@app.route('/data-log', methods=['GET'])
def data_log():
    data_array = []
    for sample in DataLog.query.all():
        sample_obj = {}
        sample_obj['sample_number'] = sample.id
        sample_obj['current_time'] = sample.time
        sample_obj['temperature'] = sample.temperature
        sample_obj['humidity'] = sample.humidity
        sample_obj['co2_content'] = sample.carbon_dioxide
        data_array.append(sample_obj)
    return data_array

def get_realtime():
    rt_time = DataLog.query.order_by(DataLog.id.desc()).first().time[0:19]
    rt_temperature = DataLog.query.order_by(DataLog.id.desc()).first().temperature
    rt_humidity = DataLog.query.order_by(DataLog.id.desc()).first().humidity
    rt_co2_level = DataLog.query.order_by(DataLog.id.desc()).first().carbon_dioxide
    return rt_time, rt_temperature, rt_humidity, rt_co2_level