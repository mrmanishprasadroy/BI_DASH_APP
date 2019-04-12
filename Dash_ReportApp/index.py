import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
import plotly.plotly as py
from plotly import graph_objs as go
import math
from app import app, server, DB
from apps import coilreport, production, stoptime

app.layout = html.Div(
    [
        # header
        html.Div([

            html.Span("PLTCM  DashBorad", className='app-title'),

            html.Div(
                html.Img(
                    src='assets/logo.png',
                    height="100%")
                , style={"float": "right", "height": "80%", "padding": "5px"})
        ],
            className="row header"
        ),

        # tabs
        html.Div([

            dcc.Tabs(
                id="tabs",
                style={"height": "20", "verticalAlign": "middle"},
                children=[
                    dcc.Tab(label="Production", value="production_tab"),
                   # dcc.Tab(label="Coil Report", value="coilreport_tab"),
                    dcc.Tab(id="stoptime_tab", label="Stop Times", value="stoptime_tab"),
                ],
                value="production_tab",
            )

        ],
            className="row tabs_div"
        ),

        # divs that save data frame for each tab
        html.Div(DB.get_stoptime().to_json(orient="split"), id="stoptime_df", style={'display': "none"}),
        html.Div(DB.get_production().to_json(orient="split"), id="production_df", style={'display': "none"}),

        # Tab content
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),

    ],
    className="row",
    style={"margin": "0%"},
)


@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "production_tab":
        return production.layout
    elif tab == "coilreport_tab":
        return coilreport.layout
    elif tab == "stoptime_tab":
        return stoptime.layout
    else:
        return production.layout


if __name__ == "__main__":
    app.run_server(host='10.182.10.162', debug=True)
