# -*- coding: utf-8 -*-
import math
import json
from datetime import date
import dateutil.parser

import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go

layout = [

    # top controls
    html.Div(
        [
            html.H3("Stop Time Tab")
        ])

]
