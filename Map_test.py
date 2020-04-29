import sys
import dash
import dash_core_components as dcc
import dash_html_components as html

import os
import pathlib
import re

import pandas as pd
from dash.dependencies import Input, Output, State


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

df_trees_properties_boro = pd.read_csv(os.path.join(APP_PATH, os.path.join(
    "data", "Trees_Properties_With_Centroids_Boro.csv")))


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

BINSB = [
    "2000-2300",
    "2301-2600",
    "2601-2900",
    "2901-3200",
    "3201-3500"
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
DEFAULT_COLORSCALEB = [
    "#f2fffb",
    "#59dab2",
    "#2bb489",
    "#188463",
    "#10523e",
]

DEFAULT_OPACITY = 0.5


colors = {
    'background': '#092a35',
    'text': '#658525',
    'text2': '#f8eeb4',
    'border': '#dae1e7',
    'chart': ['#27496d', '#00909e', '#4d4c7d']
}


def find_colorscale_by_boro(df):
    color_by_boro = ['#6a2c70' if row['borough'] == 'manhattan' else '#b83b5e' if row['borough'] == 'brooklyn' else '#f08a5d' if row['borough'] ==
                     'queens' else '#f9ed69' if row['borough'] == 'staten island' else '#3ec1d3' for index, row in df.iterrows()]
    return color_by_boro


# colorscale_by_boro = [[0, '#6a2c70'], [1, '#b83b5e'],
#                      [2, '#f08a5d'], [3, '#f9ed69'], [4, '#3ec1d3']]

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
                        html.Div([
                            html.P(children="Choose view:")
                        ], style={'display': 'inline-block', 'paddingRight': 18}),
                        html.Div([
                            dcc.RadioItems(
                                id='choiceNB',
                                options=[
                                    {'label': 'Borough View',
                                     'value': 'boroughs'},
                                    {'label': 'Neighborhood View',
                                     'value': 'neighborhoods'}
                                ],
                                # value='boroughs',
                                labelStyle={
                                    'color': colors['text'], 'backgroundColor': colors['background'],
                                    'display': 'inline-block',
                                    'paddingRight': 10}
                            )
                        ], style={'display': 'inline-block'})

                    ],
                    className='six columns',
                    style={'marginTop': '10', 'marginLeft': 20,
                           'color': colors['text']}
                ),

                html.Div(
                    [
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
                            value=None,
                            id="choiceRightGraph",
                            style={
                                'backgroundColor': colors['background'],
                                'color': colors['text']
                            }
                        )
                    ],
                    className='six columns',
                    style={'marginTop': '10', 'marginLeft': 20,
                           'backgroundColor': colors['background'],
                           'color': colors['text']}
                )
            ], className="row"
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div([
                            html.P(children="Choose feature:")
                        ], style={'display': 'inline-block'}),
                        html.Div([
                            dcc.RadioItems(
                                id='choice_feature',
                                options=[
                                    {'label': 'Trees/ sq.mile',
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
                        ], style={'display': 'inline-block'})

                    ],
                    className='six columns',
                    style={'marginTop': '10', 'marginLeft': 20,
                           'color': colors['text'],
                           'display': 'inline-block'}
                ),
            ], className="row"
        ),

        html.Div([
            html.Div([
                dcc.Graph(
                    id='mapGraph',
                    figure=dict(
                        data=[
                            dict(
                                lat=df_trees_properties["centerLat"],
                                lon=df_trees_properties["centerLong"],
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
                                zoom=9,
                            ),
                            autosize=True,
                        ),
                    ),
                )], className='six columns', style={'paddingLeft': 20, 'paddingBottom': 10}),

            html.Div([
                html.Div([
                    dcc.Graph(
                        id='rightGraph'
                    )

                ], className='row')
            ], className='six columns')
        ], className='row')
    ]))

######################################################################################################################
# map update
######################################################################################################################


@app.callback(
    Output("mapGraph", "figure"),
    [Input("choiceNB", "value"),
     Input("choice_feature", "value")],
    [State("mapGraph", "figure")],
)
def display_map(choiceNB, choice_feature, figure):
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

    if choiceNB == 'neighborhoods':
        bins = BINS
        colorscale = DEFAULT_COLORSCALE
        latitude = df_trees_properties["centerLat"]
        longitude = df_trees_properties["centerLong"]
        hover_text = df_trees_properties["hover"]
        base = "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/neighborhoods/"
    else:
        bins = BINSB
        colorscale = DEFAULT_COLORSCALEB
        latitude = df_trees_properties_boro["centerLat"]
        longitude = df_trees_properties_boro["centerLong"]
        hover_text = df_trees_properties_boro["hover"]
        base = "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/boroughs/"

    cm = dict(zip(bins, colorscale))
    data = [
        dict(
            lat=latitude,
            lon=longitude,
            text=hover_text,
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0),
        )
    ]

    for i, bin in enumerate(reversed(bins)):
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
                font=dict(color='#2cfec1'),
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
        transition={'duration': 500},
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso",
    )

    for bin in bins:
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


######################################################################################################################


@app.callback(
    Output('rightGraph', 'figure'),
    [
        Input('choiceRightGraph', 'value'),
        Input('mapGraph', 'selectedData'),
        Input('choiceNB', 'value'),
    ])
def display_selected_data(choiceRG, selectedArea, choiceNB):
    title_x = ''
    title_y = ''
    title = ''
    data = []

    if choiceNB == 'neighborhoods':
        title_part = ' neighborhoods'
        df = df_trees_properties
        key = 'ntaname'
    else:
        df = df_trees_properties_boro
        title_part = ' boroughs'
        key = 'borough'

    if selectedArea != None:
        points = selectedArea["points"]
        area_names = [str(point["text"].split("<br")[0]) for point in points]
        df_selected = df[df[key].isin(area_names)]
    else:
        df_selected = df

    if choiceRG is None or choiceRG == 'scatter_matrix':
        # data = ################################################################ scatter
        # matrix data here

        data.append({'x': df_selected.sort_values(by=['avg.landprice_thous$/acre'])[key],
                     'y': df_selected.sort_values(by=['avg.landprice_thous$/acre'])['avg.landprice_thous$/acre'],
                     'type': 'bar',
                     'text': df_selected['hover'],
                     'marker': {
                    'color': find_colorscale_by_boro(df_selected.sort_values(by=['avg.landprice_thous$/acre'])), 'opacity': 0.8, 'line': {'color': colors['border'], 'width': 1}}})
        title_x = title_part
        title_y = 'Avg Land Prices (thousands$/acre)'
        title = "Click/click-shift on the map to select areas"

    elif choiceRG == 'land_price':
        data.append({'x': df_selected.sort_values(by=['avg.landprice_thous$/acre'])[key],
                     'y': df_selected.sort_values(by=['avg.landprice_thous$/acre'])['avg.landprice_thous$/acre'],
                     'type': 'bar',
                     'text': df_selected['hover'],
                     'marker': {
                    'color': find_colorscale_by_boro(df_selected.sort_values(by=['avg.landprice_thous$/acre'])),  'opacity': 0.8, 'line': {'color': colors['border'], 'width': 1}}})
        title_x = title_part
        title_y = 'Avg Land Prices (thousands$/acre)'
        title = 'Barchart of Avg Land Prices by ' + title_part

    elif choiceRG == 'trees_per_area':
        data.append({'x': df_selected.sort_values(by=['trees/sq.mile'])[key],
                     'y': df_selected.sort_values(by=['trees/sq.mile'])['trees/sq.mile'],
                     'type': 'bar',
                     'text': df_selected['hover'],
                     'marker': {
                    'color': find_colorscale_by_boro(df_selected.sort_values(by=['trees/sq.mile'])),  'opacity': 0.8,  'line': {'color': colors['border'], 'width': 1}}})
        title_x = title_part
        title_y = 'Trees/sq.mile'
        title = 'Barchart of Number of Trees/sq.mile by ' + title_part

    elif choiceRG == 'trees_properties_sqmile':

        data.append({'x': df_selected['trees/sq.mile'],
                     'y': df_selected['properties/sq.mile'],
                     'type': 'scatterplot',
                     'mode': 'markers',
                     'text': df_selected['hover'],
                     'marker': {
                    'color': find_colorscale_by_boro(df_selected.sort_values(by=['trees/sq.mile'])), 'opacity': 0.8,  'line': {'color': colors['border'], 'width': 1}}})
        title_x = 'Trees/sq.mile'
        title_y = 'Properties/sq.mile'
        title = 'Scatterplot of Properties/sq.mile and Trees/sq.mile by'+title_part

    else:
        data.append({'x': df_selected['trees/sq.mile'],
                     'y': df_selected['area'],
                     'type': 'scatterplot',
                     'text': df_selected['hover'],
                     'mode': 'markers',
                     'marker': {
                    'color': find_colorscale_by_boro(df_selected.sort_values(by=['trees/sq.mile'])),  'opacity': 0.8,  'line': {'color': colors['border'], 'width': 1}}})
        title_x = 'Trees/sq.mile'
        title_y = 'Area (sq.mile)'
        title = 'Scatterplot of Trees/sq.mile and Areas sizes by ' + title_part

    figure = {
        'data': data,
        'layout': {
            'hovermode': 'closest',
            'transition': {'duration': 500},
            'title': title,
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text2'],
                'size': 12
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
                )),
        },

    }
    return figure


if __name__ == '__main__':

    app.run_server(debug=True)
