# -*- coding: utf-8 -*-
import math
import json
import dateutil.parser

import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.plotly as py
from plotly import graph_objs as go
from datetime import datetime as dt
from app import app, indicator, millify, df_to_table, DB


# returns pie chart that shows coils per alloycode
def alloy_source(df):
    types = df["ALLOYCODE"]
    values = df["count"]
    trace = go.Pie(
        labels=types,
        values=values,
        marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    layout = dict(margin=dict(l=15, r=10, t=0, b=65), legend=dict(orientation="h"))

    return dict(data=[trace], layout=layout)


# returns pie chart that shows width per coils
def width_source(df):
    types = df["ENTRYWIDTH"]
    values = df["count"]
    trace = go.Pie(
        labels=types,
        values=values,
        marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    layout = dict(margin=dict(l=15, r=10, t=0, b=65))

    return dict(data=[trace], layout=layout)


# returns pie chart that shows thickness per coils
def thickness_pie_source(df):
    types = df["EXITTHICK"]
    values = df["count"]
    trace = go.Pie(
        labels=types,
        values=values,
        marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    layout = dict(margin=dict(l=15, r=10, t=0, b=65))

    return dict(data=[trace], layout=layout)


def thickness_source(df):
    types = df["EXITTHICK"]
    values = df["count"]
    data = [go.Bar(y=types, x=values,
                   orientation="h")]  # x could be any column value since its a count

    layout = go.Layout(
        barmode="stack",
        margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


# function to perform date range filter
def filter_data(df, start_date, end_date):
    if start_date is not None:
        start_date = dt.strptime(start_date[:10], '%Y-%m-%d')
    if end_date is not None:
        end_date = dt.strptime(end_date[:10], '%Y-%m-%d')

    df['DTENDROLLING'] = pd.to_datetime(df['DTENDROLLING'])

    if start_date is not None:
        mask = (df['DTENDROLLING'] > start_date) & (df['DTENDROLLING'] <= end_date)
        df = df.loc[mask]
    return df


layout = [

    # top controls
    html.Div(
        [
            html.Div(
                dcc.Dropdown(
                    id="converted_leads_dropdown",
                    options=[
                        {"label": "All", "value": "A"},
                        {"label": "By day", "value": "D"},
                        {"label": "By week", "value": "W-MON"},
                        {"label": "By month", "value": "M"},
                    ],
                    value="A",
                    clearable=False,
                ),
                className="two columns",
            ),
            html.Div(
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=dt(2017, 8, 5),
                    max_date_allowed=dt.now(),
                    initial_visible_month=dt.now(),
                    end_date=dt.now()
                ),
                className="four columns",
            ),

            html.Div(
                dcc.RangeSlider(
                    id='thicknessslider',
                    marks={i: 'Exit Thickness  {} mm'.format(i) for i in range(0, 4)},
                    min=-0,
                    max=3,
                    step=0.1,
                    value=[0, 3]
                ),
                className="four columns"
            ),
        ],
        className="row",
        style={"marginBottom": "10"},
    ),
    # indicators row div
    html.Div(
        [
            indicator(
                "#00cc96", "Coils Count", "left_leads_indicator"
            ),
            indicator(
                "#119DFF", "Total Weight in ton", "middle_leads_indicator"
            ),
            indicator(
                "#EF553B",
                "Tonnage Per coil in kg",
                "right_leads_indicator",
            ),
        ],
        className="row",
    ),
    # charts row div
    html.Div(
        [
            html.Div(
                [
                    html.P("Coils count with Alloy Code"),
                    dcc.Graph(
                        id="alloy_source",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="four columns chart_div"
            ),
            html.Div(
                [
                    html.P("Coils count with Entry width"),
                    dcc.Graph(
                        id="width_source",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="four columns chart_div"
            ),

            html.Div(
                [
                    html.P("Coils count with Exit Thickness"),
                    dcc.Graph(
                        id="thickness_leads",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="four columns chart_div"
            ),
        ],
        className="row",
        style={"marginTop": "5"},

    ),

    # table div
    html.Div(
        id="production_table",
        className="row",
        style={
            "maxHeight": "320px",
            "overflowY": "scroll",
            "padding": "8",
            "marginTop": "5",
            "backgroundColor": "white",
            "border": "1px solid #C8D4E3",
            "borderRadius": "3px"

        },

    ),
]


# updates left indicator based on df updates
@app.callback(
    Output("left_leads_indicator", "children"),
    [Input("production_df", "children"),
     Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date")]
)
def left_leads_indicator_callback(df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if start_date is not None:
        df = filter_data(df, start_date, end_date)
    coil_count = len(df)
    return coil_count


# updates middle indicator based on df updates
@app.callback(
    Output("middle_leads_indicator", "children"),
    [Input("production_df", "children"),
     Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date")]
)
def middle_leads_indicator_callback(df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if start_date is not None:
        df = filter_data(df, start_date, end_date)
    return math.floor((df['EXITWEIGHTMEAS'].aggregate(sum)) / 1000)


# updates right indicator based on df updates
@app.callback(
    Output("right_leads_indicator", "children"),
    [Input("production_df", "children"),
     Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date")]
)
def right_leads_indicator_callback(df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if start_date is not None:
        df = filter_data(df, start_date, end_date)
    coil_count = len(df)
    tot_weight = df['EXITWEIGHTMEAS'].aggregate(sum)
    return math.floor(tot_weight / coil_count)


# update pie chart figure df updates
@app.callback(
    Output("alloy_source", "figure"),
    [Input("converted_leads_dropdown", "value"),
     Input("production_df", "children"),
     Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date")]
)
def alloy_source_callback(status, df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if start_date is not None:
        df = filter_data(df, start_date, end_date)
    allycode_stats = df.groupby('ALLOYCODE')['COILIDOUT'].describe().reset_index()
    return alloy_source(allycode_stats)


# update pie chart figure df updates
@app.callback(
    Output("width_source", "figure"),
    [Input("converted_leads_dropdown", "value"),
     Input("production_df", "children"),
     Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date")]
)
def width_source_callback(status, df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if start_date is not None:
        df = filter_data(df, start_date, end_date)
    width_stats = df.groupby('ENTRYWIDTH')['COILIDOUT'].describe().reset_index()
    return width_source(width_stats)


# update pie chart figure df updates
@app.callback(
    Output("thickness_leads", "figure"),
    [Input("thicknessslider", "value"),
     Input("production_df", "children"),
     Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date")]
)
def thickness_source_callback(value, df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if start_date is not None:
        df = filter_data(df, start_date, end_date)
    thickness_stats = df.groupby('EXITTHICK')['COILIDOUT'].describe().reset_index()
    thickness_stats = thickness_stats[thickness_stats['EXITTHICK'] <= value[1]]
    return thickness_source(thickness_stats)


# update table based on drop down value and df updates
@app.callback(
    Output("production_table", "children"),
    [Input("production_df", "children"),
     Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date")],
)
def leads_table_callback(df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    df['DTDEPARTURE'] = pd.to_datetime(df['DTDEPARTURE'])
    df['DTSTARTROLL'] = pd.to_datetime(df['DTSTARTROLL'])
    df['DTENDROLLING'] = pd.to_datetime(df['DTENDROLLING'])
    if start_date is not None:
        df = filter_data(df, start_date, end_date)
    datatable = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        n_fixed_rows=1,
        # filtering=True,
        sorting=True,
        style_cell={'width': '150px', 'padding': '5px', 'textAlign': 'center'},
        style_cell_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': '#3D9970',
        }] + [
                                   {
                                       'if': {'column_id': c},
                                       'textAlign': 'left'
                                   } for c in ['COILIDOUT', 'COILIDIN', 'ALLOYCODE']
                               ],
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        style_table={
            'maxHeight': '280px',
            'overflowY': 'scroll',
            'border': 'thin lightgrey solid'
        },
    )
    return datatable
