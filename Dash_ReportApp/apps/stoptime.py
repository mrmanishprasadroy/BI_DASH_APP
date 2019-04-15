# -*- coding: utf-8 -*-

from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
from app import app, indicator, DB
from dash.dependencies import Input, Output, State
from plotly import graph_objs as go


def date_source(df):
    types = df["DATE"]
    values = df["mean"]
    data = [go.Bar(x=types, y=values,
                   orientation="v")]  # x could be any column value since its a count

    layout = go.Layout(
        barmode="stack",
        margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


global_df = DB.get_stoptime()

layout = [

    html.Div(
        [
            html.Div(
                dcc.DatePickerRange(
                    id='date-range',
                    min_date_allowed=dt(2017, 8, 5),
                    max_date_allowed=dt.now(),
                    initial_visible_month=dt.now(),
                    end_date=dt.now()
                ),
                className="four columns",
            ),
            html.Div(html.Button(id='submit-button', n_clicks=0, children='Submit'), className="two columns"),
        ],
        className="row",
        style={"marginBottom": "10"},
    ),

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
                    html.P("Per Day Avg Delay"),
                    dcc.Graph(
                        id="date_analysis",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="twelve columns chart_div"
            ),

            # Hidden div inside the app that stores the intermediate value
            html.Div(id='intermediate-value', style={'display': 'none'}),

        ],
        className="row",
        style={"marginTop": "5"},

    ),
    dcc.Input(id="input-1", value='Input triggers local spinner', style={'display': 'none'}),
    html.Div(id="parttime_df", style={'display': "none"}),
    # dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-1")], type="default"),

    # table div
    dcc.Loading(id='table-view', children=html.Div(
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
    ), type="default"),

]


# update hidden div data block
@app.callback(
    Output('parttime_df', 'children'),
    [Input("stoptime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def store_data(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if n_clicks > 0:
        df_1 = df.set_index('DATE')
        df = df_1.loc[start_date:end_date]
        cleaned_df = df.reset_index()
    else:
        cleaned_df = df
    return cleaned_df.to_json(orient="split")


# updates left indicator based on df updates
@app.callback(
    Output("left_PL_indicator", "children"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def left_leads_indicator_callback(df, n_clicks,start_date, end_date):
    df = pd.read_json(df, orient="split")
    df_stats = df.groupby('PLANT')['DURATION'].sum()
    return np.ceil(df_stats[1])


# updates middle  indicator based on df updates
@app.callback(
    Output("middle_TCM_indicator", "children"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def left_leads_indicator_callback(df, n_clicks,start_date, end_date):
    df = pd.read_json(df, orient="split")
    df_stats = df.groupby('PLANT')['DURATION'].sum()
    return np.ceil(df_stats[2])


# updates Right  indicator based on df updates
@app.callback(
    Output("right_PLTCM_indicator", "children"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def left_leads_indicator_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    df_stats = df.groupby('PLANT')['DURATION'].sum()
    return np.ceil(df_stats[3])


# update table based on drop down value and df updates
@app.callback(
    Output("stop_table", "children"),
    [Input("parttime_df", "children"), Input("input-1", "value"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def leads_table_callback(df, value, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    df = df.groupby('DATE')['DURATION'].describe().reset_index()

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


# update Bar chart figure df updates
@app.callback(
    Output("date_analysis", "figure"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def by_date_source_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    df = df.groupby('DATE')['DURATION'].describe().reset_index()
    figure = date_source(df)
    return figure


