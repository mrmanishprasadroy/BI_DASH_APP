# -*- coding: utf-8 -*-
import math
import json
from datetime import date
import dateutil.parser

import pandas as pd
import numpy as np
import flask
import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go
from datetime import datetime as dt
from app import app, indicator, millify, df_to_table, DB

layout = [

    # indicators row div
    html.Div(
        [
            indicator(
                "#00cc96", "Total Delay Duartion PL in Min", "left_PL_indicator"
            ),
            indicator(
                "#119DFF", "Total Delay Duartion TCM in Min", "middle_TCM_indicator"
            ),
            indicator(
                "#EF553B",
                "Total Delay Duartion PLTCM in Min",
                "right_PLTCM_indicator",
            ),
        ],
        className='row',
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
                className="twelve columns chart_div"
            ),

        ],
        className="row",
        style={"marginTop": "5"},

    ),

    # table div
    html.Div(
        id="stop_table",
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
    Output("left_PL_indicator", "children"),
    [Input("stoptime_df", "children")]
)
def left_leads_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    df_stats = df.groupby('PLANT')['DURATION'].sum()
    return np.ceil(df_stats[0])


# updates middle  indicator based on df updates
@app.callback(
    Output("middle_TCM_indicator", "children"),
    [Input("stoptime_df", "children")]
)
def left_leads_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    df_stats = df.groupby('PLANT')['DURATION'].sum()
    return np.ceil(df_stats[1])


# updates Right  indicator based on df updates
@app.callback(
    Output("right_PLTCM_indicator", "children"),
    [Input("stoptime_df", "children")]
)
def left_leads_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    df_stats = df.groupby('PLANT')['DURATION'].sum()
    return np.ceil(df_stats[2])


# update table based on drop down value and df updates
@app.callback(
    Output("stop_table", "children"),
    [Input("stoptime_df", "children")],
)
def leads_table_callback(df):
    df = pd.read_json(df, orient="split")
    df = df.groupby('PLANT')['DURATION'].describe().reset_index()

    datatable = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        n_fixed_rows=1,
        # filtering=True,
        sorting=True,
        style_cell={'width': '150px', 'padding': '5px', 'textAlign': 'center'},
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        style_cell_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': '#3D9970',
        }],
        style_table={
            'maxHeight': '280px',
            'overflowY': 'scroll',
            'border': 'thin lightgrey solid'
        },
    )
    return datatable

