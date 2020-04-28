import sys
import dash
import dash_core_components as dcc
import dash_html_components as html

import os
import pathlib
import re

import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf


# Initialize app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets)

server = app.server

# Mapbox info
mapbox_access_token = 'pk.eyJ1IjoibWlzaGtpY2UiLCJhIjoiY2s5MG94bWRoMDQxdjNmcHI1aWI1YnFkYyJ9.eFsHqEMYY7qxa0Pb9USCtQ'
mapbox_style = "mapbox://styles/mishkice/ck98qopeo05k21ipc1atfdn8h"

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_trees_properties = pd.read_csv(
    os.path.join(APP_PATH, os.path.join(
        "data", "Trees_Properties_With_Centroids.csv"))
)

df_trees_properties = df_trees_properties[(
    df_trees_properties['avg.landprice_thous$/acre'] > 0) & (df_trees_properties['avg.landprice_thous$/acre'] < 1000)]

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

# App layout
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src=app.get_asset_url(
                    "tree_house_image.png")),
                html.H1(children='NYC Trees & Properties ',
                        style={
                            'textAlign': 'center',
                            'color': colors['text'],
                            'paddingTop':30,
                            'paddingBottom': 30
                        }
                        ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                dcc.RadioItems(
                                    id='choiceMap',
                                    options=[
                                        {'label': 'Trees/sq.mile',
                                         'value': 'Trees/sq.mile'},
                                        {'label': 'Avg land price',
                                         'value': 'Avg land price'},
                                    ],
                                    value='Trees/sq.mile',
                                    labelStyle={
                                        'color': colors['text'], 'backgroundColor': colors['background'],
                                        'display': 'inline-block',
                                        'paddingRight': 10}
                                )
                            ],
                        ),
                        html.Div(
                            id="map-container",
                            children=[
                                html.P(
                                    "Choropleth Map of {0}".format(
                                        "Trees/sq.mile"
                                    ),
                                    id="mapTitle",
                                ),
                                ##########################################
                                dcc.Graph(
                                    id="mapGraph",
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
                                                    lat=40.7342, lon=-73.91251
                                                ),
                                                pitch=0,
                                                zoom=10,
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Scatterplot of Trees/sq.mile and Properties/sq.mile",
                                    "value": "trees_properties_sqmile",
                                },
                                {
                                    "label": "Scatterplot of Trees/sq.mile and Areas sizes",
                                    "value": "trees_areas",
                                },
                                {
                                    "label": "PieChart of Tree Speices ",
                                    "value": "tree_speices",
                                },
                                {
                                    "label": "Barchart of Avg Land Prices ",
                                    "value": "land_price",
                                },
                                {
                                    "label": "Barchart of Trees/sq.mile",
                                    "value": "trees_per_area",
                                },
                            ],
                            value="trees_properties_sqmile",
                            id="choiceRightGraph",
                        ),
                        dcc.Graph(
                            id="rightGraph",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("mapGraph", "figure"),
    [Input("choiceMap", "value")],
    [State("mapGraph", "figure")],
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
            marker=dict(size=5, color="white", opacity=0),
        )
    ]

    annotations = [
        dict(
            showarrow=False,
            align="right",
            #text="<b>Age-adjusted death rate<br>per county per year</b>",
            font=dict(color="#2cfec1"),
            bgcolor="#1f2630",
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
                bgcolor="#1f2630",
                font=dict(color="#2cfec1"),
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
        clickmode="select",
    )

    base = "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/"
    for bin in BINS:
        geo_layer = dict(
            sourcetype="geojson",
            source=base + bin + ".geojson",
            type="fill",
            color=cm[bin],
            opacity=DEFAULT_OPACITY,
            fill=dict(outlinecolor="#afafaf"),
        )
        layout["mapbox"]["layers"].append(geo_layer)

    fig = dict(data=data, layout=layout)
    return fig


@app.callback(Output("mapTitle", "children"),
              [Input("choiceMap", "value")])
def update_map_title(choiceMap):
    return "Choropleth Map of {0}".format(
        choiceMap
    )


@app.callback(
    Output("rightGraph", "figure"),
    [
        Input("mapGraph", "selectedData"),
        Input("choiceRightGraph", "value"),
        #Input("choiceMap", "value"),
    ],
)
def display_selected_data(selectedData, choiceRG):
    if choiceRG != None:
        point = selectedData["points"]
        ntaname = str(point["text"].split("<br>")[0])
        neighborhood = df_trees_properties[df_trees_properties["ntaname"].isin(
            ntaname)]

    title_x = ''
    title_y = ''
    title = ''
    data = []
    if choiceRG == None or choiceRG == 'land_price':
        data.append({'x': df_trees_properties['ntaname'],
                     'y': df_trees_properties['avg.landprice_thous$/acre'],
                     'type': 'bar',
                     'marker': {
                    'color': colors['chart'][0], 'line': {'color': colors['border'], 'width': 1}}})
        title_x = 'neighborhoods'
        title_y = 'Avg Land Prices (thousands$/acre)'
        title = 'Barchart of Avg Land Prices by Neighborhood'
    elif choiceRG == 'trees_per_area':
        data.append({'x': df_trees_properties['ntaname'],
                     'y': df_trees_properties['trees/sq.mile'],
                     'type': 'bar',
                     'marker': {
                    'color': colors['chart'][0], 'line': {'color': colors['border'], 'width': 1}}})
        title_x = 'neighborhoods'
        title_y = 'Trees/sq.mile'
        title = 'Barchart of Number of Trees/sq.mile'
    elif choiceRG == 'trees_properties_sqmile':
        data.append({'x': df_trees_properties['trees/sq.mile'],
                     'y': df_trees_properties['properties/sq.mile'],
                     'type': 'scatterplot',
                     'marker': {
                    'color': colors['chart'][0], 'line': {'color': colors['border'], 'width': 1}}})
        title_x = 'Trees/sq.mile'
        title_y = 'Properties/sq.mile'
        title = 'Scatterplot of Properties/sq.mile'
    elif choiceRG == 'trees_areas':
        data.append({'x': df_trees_properties['area'],
                     'y': df_trees_properties['trees/sq.mile'],
                     'type': 'scatterplot',
                     'marker': {
                    'color': colors['chart'][0], 'line': {'color': colors['border'], 'width': 1}}})
        title_x = 'Area (sq.mile)'
        title_y = 'Trees/sq.mile'
        title = 'Scatterplot of Trees/sq.mile and Areas sizes'
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


if __name__ == "__main__":
    app.run_server(debug=True)
