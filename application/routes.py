from flask import render_template, jsonify
import json
import pandas as pd
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import csv

from __init__ import app, db
from models import Data_Log

from application.models import Realtime_Data

@app.route('/', methods=['GET'])
def index():
    # Temporary - Used for testing display of plots on frontend
    sample_nums = []
    time_axis = []
    temp_axis = []
    humidity_axis = []
    co2_axis = []
    with open('../data/test_set.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each in csvreader:
            sample_nums.append(each[0])
            time_axis.append(pd.to_datetime(each[1]))
            temp_axis.append(float(each[2]))
            humidity_axis.append(float(each[3]))
            co2_axis.append(float(each[4]))

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.075,
        subplot_titles=('Temperature', 'Humidity', 'CO2 Content')
        )

    fig.add_trace(go.Scatter(x=time_axis, y=temp_axis),
        row=1, col=1)
        
    fig.add_trace(go.Scatter(x=time_axis, y=humidity_axis),
        row=2, col=1)
        
    fig.add_trace(go.Scatter(x=time_axis, y=co2_axis),
        row=3, col=1)
        
    fig.update_layout(
        height=800, width=1200,
        showlegend=False,
        title_text='Fruiting Room Environment Data'
        )
    fig.show()
    graph_JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    realtime = get_realtime()

    return render_template('index.html', graph_JSON=graph_JSON, realtime=realtime)

@app.route('/data-log', methods=['GET'])
def data_log():
    data_array = []
    for sample in Data_Log.query.all():
        sample_obj = {}
        sample_obj['sample_number'] = sample.id
        sample_obj['current_time'] = sample.time
        sample_obj['temperature'] = sample.temperature
        sample_obj['humidity'] = sample.humidity
        sample_obj['co2_content'] = sample.carbon_dioxide
        data_array.append(sample_obj)
    return jsonify({'fruiting room data': data_array})

def get_realtime():
    rt_time = Realtime_Data.query.first().time
    rt_temperature = Realtime_Data.query.first().temperature
    rt_humidity = Realtime_Data.query.first().humidity
    rt_co2_level = Realtime_Data.query.first().carbon_dioxide
    return (rt_time, rt_temperature, rt_humidity, rt_co2_level)