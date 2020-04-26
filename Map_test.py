import sys
import socketserver
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

import os
import pathlib
import re

from flask import Flask, request

import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf
from chart_studio.api.v2.utils import request


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets)


mapbox_access_token = 'pk.eyJ1IjoibWlzaGtpY2UiLCJhIjoiY2s5MG94bWRoMDQxdjNmcHI1aWI1YnFkYyJ9.eFsHqEMYY7qxa0Pb9USCtQ'
mapbox_style = "mapbox://styles/mishkice/ck98qopeo05k21ipc1atfdn8h"

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_trees_properties = pd.read_csv(
    os.path.join(APP_PATH, os.path.join(
        "data", "Trees_Properties_With_Centroids.csv"))
)

BINS = [
    "0-500",
    "501-1000",
    "1001-1500",
    "1501-2000",
    "2001-2500",
    "2501-3000",
    "3001-3500",
    "3501-4000",
    "4001-4500",
    "4501-5000"
]

DEFAULT_COLORSCALE = [
    "#f2fffb",
    "#98ffe0",
    "#6df0c8",
    "#59dab2",
    "#45d0a5",
    "#2bb489",
    "#1e906d",
    "#188463",
    "#157658",
    "#10523e",
]
DEFAULT_OPACITY = 0.8


colors = {
    'background': '#092a35',
    'text': '#658525',
    'text2': '#f8eeb4',
    'border': '#dae1e7',
    'chart': ['#27496d', '#00909e', '#4d4c7d']
}

layout_map = dict(
    autosize=True,
    height=500,
    font=dict(color=colors['text']),
    titlefont=dict(color=colors['text'], size='14'),
    hovermode="closest",
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    legend=dict(font=dict(size=10), orientation='h'),
    title='Empty map',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="mapbox://styles/mishkice/ck98qopeo05k21ipc1atfdn8h",
        center=dict(
            lon=-73.91251,
            lat=40.7342
        ),
        zoom=10,
    ))


app.layout = html.Div(
    html.Div(style={'backgroundColor': colors['background']}, children=[

        html.Div([
            html.H1(
                children='NYC Trees & Properties ',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'paddingTop':30,
                    'paddingBottom': 30
                })
        ], className='row'),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id='choice',
                            options=[
                                {'label': 'trees/sq.mile & properties/sq.mile',
                                    'value': 'trees_properties'},
                                {'label': 'trees/sq.mile & area of neighborhood',
                                    'value': 'trees_area'},
                            ],
                            placeholder='Select features',
                            style={
                                'color': colors['text'], 'backgroundColor': colors['background']}
                        ),
                        html.Div(id='dd-output-container')
                    ],
                    className='six columns',
                    style={'marginTop': '10', 'marginLeft': 20,
                           'color': colors['text']}
                ),
            ], className="row"
        ),

        html.Div([
            html.Div([
                dcc.Graph(
                    id='map_graph',
                    figure=dict(
                        data=[
                            dict(
                                lat=df_trees_properties["center"][1],
                                lon=df_trees_properties["center"][0],
                                text=df_trees_properties["hover"],
                                type="scattermapbox",
                            )
                        ],
                        layout=dict(
                            mapbox=dict(
                                layers=[],
                                accesstoken=mapbox_access_token,
                                style=mapbox_style,
                                center=dict(
                                    lat=40.7342,
                                    lon=-73.91251
                                ),
                                pitch=0,
                                zoom=10,
                            ),
                            autosize=True,
                        ),
                    ),
                )], className='six columns'),

            html.Div([
                html.Div([
                    dcc.Graph(
                        id='right_graph'
                    )

                ], className='row')
            ], className='six columns')
        ], className='row')
    ]))

##################################################################
# map part
##################################################################


@app.callback(
    Output("map_graph", "figure"),
    [Input("choice", "value")],
    [State("map_graph", "figure")],
)
def display_map(selector, figure):
    cm = dict(zip(BINS, DEFAULT_COLORSCALE))

    data = [
        dict(
            lat=df_trees_properties["center"][1],
            lon=df_trees_properties["center"][0],
            text=df_trees_properties["hover"],
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0.3),
        )
    ]

    annotations = [
        dict(
            showarrow=False,
            align="right",
            text="Trees/sq.mile",
            font=dict(color="#2cfec1"),
            bgcolor=colors['background'],
            x=0.95,
            y=0.95,
        )
    ]

    for i, bin in enumerate(reversed(BINS)):
        color = cm[bin]
        annotations.append(
            dict(
                arrowcolor=color,
                text=bin,
                x=0.95,
                y=0.85 - (i / 20),
                ax=-60,
                ay=0,
                arrowwidth=5,
                arrowhead=0,
                bgcolor=colors['background'],
                font=dict(color=colors['text']),
            )
        )

    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = (40.7342,)
        lon = (-73.91251,)
        zoom = 10

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            style=mapbox_style,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso",
    )

    base = "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/"
    for bin in BINS:
        geo_layer = dict(
            sourcetype="geojson",
            source=base + bin + ".geojson",
            type="fill",
            color=cm[bin],
            opacity=DEFAULT_OPACITY,
            # CHANGE THIS
            fill=dict(outlinecolor="#afafaf"),
        )
        layout["mapbox"]["layers"].append(geo_layer)

    fig = dict(data=data, layout=layout)
    return fig
################################################################################################################


@app.callback(
    dash.dependencies.Output('right_graph', 'figure'),
    [dash.dependencies.Input('choice', 'value')])
def update_image_src(selector):
    title_x = ''
    title_y = ''
    title = ''
    data = []
    if selector == None or selector == 'trees_properties':
        data.append({'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF', 'marker': {
                    'color': colors['chart'][0], 'line': {'color': colors['border'], 'width': 1}}})
        title_x = 'Trees/sq.mile'
        title_y = 'Properties/sq.mile'
        title = 'Trees/sq.mile & Properties/sq.mile'
    if selector == 'trees_area':
        data.append({'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal', 'marker': {
                    'color': colors['chart'][0], 'line': {'color': colors['border'], 'width': 1}}})
        title_x = 'Trees/sq.mile'
        title_y = 'Areas of neighborhoods'
        title = 'Trees/sq.mile & Areas of Neighborhoods'
    figure = {
        'data': data,
        'layout': {
            'title': title,
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text'],
                'size': 16
            },
            'xaxis': dict(
                title=title_x,
                titlefont=dict(
                    size=14,
                    color=colors['text2']
                )),
            'yaxis': dict(
                title=title_y,
                titlefont=dict(
                    size=14,
                    color=colors['text2']
                ))
        }
    }
    return figure


if __name__ == '__main__':

    app.run_server(debug=True)
