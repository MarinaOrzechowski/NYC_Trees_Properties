import os
import pathlib
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr, spearmanr
import numpy as np
import pandas as pd
import re


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


mapbox_access_token = 'pk.eyJ1IjoibWlzaGtpY2UiLCJhIjoiY2s5MG94bWRoMDQxdjNmcHI1aWI1YnFkYyJ9.eFsHqEMYY7qxa0Pb9USCtQ'
mapbox_style = "mapbox://styles/mishkice/ck98qopeo05k21ipc1atfdn8h"

# Load data

df_trees_properties = pd.read_csv(
    "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/Trees_Properties_With_Centroids.csv")

df_trees_properties_boro = pd.read_csv(
    "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/Trees_Properties_With_Centroids_Boro.csv")

df_species = pd.read_csv(
    "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/GroupedTreesDataSpecies.csv")

# trees neighborhoods bins
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
# trees boroughs bins
BINSB = [
    "2000-2300",
    "2301-2600",
    "2601-2900",
    "2901-3200",
    "3201-3500"
]
# prices neighborhoods bins
BINS_P = [
    "0-20",
    "21-40",
    "41-60",
    "61-80",
    "81-100",
    "above 100"
]
# prices boroughs bins
BINSB_P = [
    "0-50",
    "51-100",
    "151-200",
    "above 200"
]

# trees neighborhoods colors
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
# trees boroughs colors
DEFAULT_COLORSCALEB = [
    "#f2fffb",
    "#59dab2",
    "#2bb489",
    "#188463",
    "#10523e",
]
# prices neighborhoods colors
DEFAULT_COLORSCALE_P = [
    "#feedde",
    "#fdd0a2",
    "#fdae6b",
    "#fd8d3c",
    "#e6550d",
    "#a63603"
]
# prices boroughs colors
DEFAULT_COLORSCALEB_P = [
    "#feedde",
    "#fdbe85",
    "#fd8d3c",
    "#e6550d",
    "#a63603",
]

DEFAULT_OPACITY = 0.8


colors = {
    'background': '#092a35',
    'text': '#769c2a',
    'text2': '#f8eeb4',
    'border': '#dae1e7',
    'chart': ['#27496d', '#00909e', '#4d4c7d']
}

# function to assign colors to markers by boroughs


def find_colorscale_by_boro(df):
    color_by_boro = ['#6a2c70' if row['borough'] == 'manhattan' else '#b83b5e' if row['borough'] == 'brooklyn' else '#f08a5d' if row['borough'] ==
                     'queens' else '#f9ed69' if row['borough'] == 'staten island' else '#3ec1d3' for index, row in df.iterrows()]
    return color_by_boro


colorscale_by_boro = ['#6a2c70', '#b83b5e', '#f08a5d', '#f9ed69', '#3ec1d3']


# page layout
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
                    style={'marginTop': 0, 'marginLeft': '2%',
                           'color': colors['text']}
                ),
                html.Div(
                    [
                        html.Div([
                            html.H6(
                                children="Pairplot Graph of Trees&Properties attributes")
                        ], style={'display': 'inline-block', 'marginLeft': 100})

                    ],
                    className='six columns',
                    style={'marginTop': 0, 'marginLeft': 20,
                           'color': colors['text'],
                           'fontsize': 14,
                           'display': 'inline-block'}
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
                    style={'marginTop': 0, 'marginLeft': '2%',
                           'color': colors['text'],
                           'display': 'inline-block'}
                )
            ], className="row"
        ),
        ######################################
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
                            autosize=False,
                        ),
                    ),
                )], className='six columns', style={'width': '40%', 'paddingLeft': '2%', 'paddingBottom': 10, 'marginBottom': 10}),  # left half ends here

            html.Div([
                html.Div([
                    dcc.Graph(
                        id='scatter_matrix'
                    )

                ], className='row'),
                html.Div([
                    dcc.Dropdown(
                        options=[
                            {
                                "label": "Scatterplot of Trees/sq.mile and Properties/sq.mile",
                                "value": "trees_properties_sqmile",
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

                ], className='row', style={'marginTop': '20', 'paddingTop': 30,
                                           'backgroundColor': colors['background'],
                                           'color': colors['text']}),

                html.Div([
                    dcc.Graph(
                        id='rightGraph'
                    )

                ], className='row')

            ], className='six columns', style={'width': '50%', 'paddingLeft': '3%', 'paddingRight': '1%', 'marginTop': 0, 'paddingTop': 0})  # right half ends here

        ], className='row', style={'width': '100%'}),  # big row ends here
    ]))

# callbacks

######################################################################################################################
# map callback
######################################################################################################################


@ app.callback(
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

    if choiceNB == 'neighborhoods' and choice_feature == 'Trees/sq.mile':
        bins = BINS
        colorscale = DEFAULT_COLORSCALE
        latitude = df_trees_properties["centerLat"]
        longitude = df_trees_properties["centerLong"]
        hover_text = df_trees_properties["hover"]
        base = "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/neighborhoods/trees_per_sqmile/"

    elif choiceNB == 'neighborhoods':
        bins = BINS_P
        colorscale = DEFAULT_COLORSCALE_P
        latitude = df_trees_properties["centerLat"]
        longitude = df_trees_properties["centerLong"]
        hover_text = df_trees_properties["hover"]
        base = "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/neighborhoods/land_price/"

    elif choice_feature != 'Avg land price':
        bins = BINSB
        colorscale = DEFAULT_COLORSCALEB
        latitude = df_trees_properties_boro["centerLat"]
        longitude = df_trees_properties_boro["centerLong"]
        hover_text = df_trees_properties_boro["hover"]
        base = "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/boroughs/trees_per_sqmile/"

    else:
        bins = BINSB_P
        colorscale = DEFAULT_COLORSCALEB_P
        latitude = df_trees_properties_boro["centerLat"]
        longitude = df_trees_properties_boro["centerLong"]
        hover_text = df_trees_properties_boro["hover"]
        base = "https://raw.githubusercontent.com/MarinaOrzechowski/NYC_Trees_Properties/master/data/boroughs/land_price/"

    cm = dict(zip(bins, colorscale))
    data = [
        dict(
            lat=latitude,
            lon=longitude,
            text=hover_text,
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="black", opacity=0),
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
        height=900,
        transition={'duration': 500},
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso"
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
# scattermatrix callback
######################################################################################################################
@app.callback(
    Output('scatter_matrix', 'figure'),
    [
        Input('mapGraph', 'selectedData'),
        Input('choiceNB', 'value')
    ])
def display_selected_data(selectedArea, choiceNB):

    if choiceNB == 'boroughs':
        df_selected = df_trees_properties_boro
        title_part = ' boroughs'
        key = 'borough'

    else:
        title_part = ' neighborhoods'
        df_selected = df_trees_properties
        key = 'ntaname'

    font_ann = dict(
        size=10,
        color=colors['text']
    )

    if selectedArea is not None:
        points = selectedArea["points"]
        area_names = [str(point["text"].split("<br")[0])
                      for point in points]
        df_selected = df_selected[df_selected[key].isin(area_names)]

    index_vals = df_selected['borough'].astype('category').cat.codes
    coef_list = []

    # find pearson coeff and p_value for each pair of attributes
    pairs = [['trees/sq.mile', 'avg.landprice_thous$/acre'], ['trees/sq.mile',
                                                              'properties/sq.mile'], ['avg.landprice_thous$/acre', 'properties/sq.mile']]
    flag = True
    for pair in pairs:
        if len(df_selected[pair[0]]) >= 2 and len(df_selected[pair[1]]) >= 2:
            coef_list.append(
                pearsonr(df_selected[pair[0]], df_selected[pair[1]]))
        else:
            flag = False
    if flag:
        ann = [
            dict(
                x=5000,
                y=6000,
                xref="x2",
                yref="y1",
                font=font_ann,
                text="PCC: " +
                str(round(coef_list[0][0], 2)) + "<br>p: " +
                ('{:0.1e}'.format(coef_list[0][1])),
                showarrow=False,

            ),
            dict(
                x=6000,
                y=5000,
                xref="x1",
                yref="y2",
                font=font_ann,
                text="PCC: " +
                str(round(coef_list[0][0], 2)) + "<br>p: " +
                ('{:0.1e}'.format(coef_list[0][1])),
                showarrow=False,
            ),
            dict(
                x=14000,
                y=6000,
                xref="x3",
                yref="y1",
                font=font_ann,
                text="PCC: " +
                str(round(coef_list[1][0], 2)) + "<br>p: " +
                ('{:0.1e}'.format(coef_list[1][1])),
                showarrow=False,
            ),
            dict(
                x=6000,
                y=14000,
                xref="x1",
                yref="y3",
                font=font_ann,
                text="PCC: " +
                str(round(coef_list[1][0], 2)) + "<br>p: " +
                ('{:0.1e}'.format(coef_list[1][1])),
                showarrow=False,
            ),
            dict(
                x=14000,
                y=6000,
                xref="x3",
                yref="y2",
                font=font_ann,
                text="PCC: " +
                str(round(coef_list[2][0], 2)) + "<br>p: " +
                ('{:0.1e}'.format(coef_list[2][1])),
                showarrow=False,
            ),
            dict(
                x=6000,
                y=14000,
                xref="x2",
                yref="y3",
                font=font_ann,
                text="PCC: " +
                str(round(coef_list[2][0], 2)) + "<br>p: " +
                ('{:0.1e}'.format(coef_list[2][1])),
                showarrow=False,
            ),

        ]
    else:
        ann = []

    axisd = dict(showline=True,
                 zeroline=False,
                 gridcolor='#104752',
                 showticklabels=True)

    # here we build a scatter matrix, and add annotations for each subgraph
    layout = go.Layout(
        dragmode='select',

        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        autosize=False,
        hovermode='closest',
        font=dict(color=colors['text'], size=12),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        xaxis1=dict(axisd),
        xaxis2=dict(axisd),
        xaxis3=dict(axisd),
        xaxis4=dict(axisd),
        yaxis1=dict(axisd),
        yaxis2=dict(axisd),
        yaxis3=dict(axisd),
        yaxis4=dict(axisd),
        annotations=ann)

    fig = go.Figure(data=go.Splom(
        dimensions=[dict(label='trees/sq.mile',
                         values=df_selected['trees/sq.mile']),
                    dict(label='avg.landprice($K/A)',
                         values=df_selected['avg.landprice_thous$/acre']),
                    dict(label='properties/sq.mile',
                         values=df_selected['properties/sq.mile']),
                    ],
        text=(df_selected[key]+': '+df_selected['borough']
              if key == 'ntaname' else df_selected[key]),
        hoverinfo="x+y+text",
        # showlegend=True,
        marker=dict(color=index_vals,
                    showscale=False,  # colors encode categorical variables
                    line_color='white', line_width=0.4),
        diagonal=dict(visible=True)
    ), layout=layout
    )

    return fig


#####################################################################################################################
# rightGraph callback
#####################################################################################################################
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

    if selectedArea is not None:
        points = selectedArea["points"]
        area_names = [str(point["text"].split("<br")[0]) for point in points]
        df_selected = df[df[key].isin(area_names)]
    else:
        df_selected = df

    if choiceRG is None or choiceRG == 'land_price':
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
        if selectedArea is not None:
            # leave only selected areas
            df_selected = df_species[df_species[key].isin(
                area_names)].sort_values('spc_per', ascending=False)

        else:
            df_selected = df_species.sort_values(
                'spc_per', ascending=False)

        # find most species with biggest count number, sort in desc order
        grouped = df_selected.groupby(['spc_common']).sum(
        ).sort_values('count', ascending=False)
        total = grouped['count'].sum()
        # find percent for each type of trees (will remain in desc order)
        grouped['prc'] = grouped['count']/total*100
        grouped.reset_index(inplace=True)
        # add row 'other' which includes info about all species except 5 most frequent
        grouped = grouped.append({'spc_common': 'other', 'count': total-grouped['count'][:10].sum(
        ), 'prc': 100 - grouped['prc'][:10].sum()}, ignore_index=True)
        # sort data again so 'other' row takes correct place
        grouped = grouped.sort_values('prc', ascending=False)

        piechart = go.Figure(data=[go.Pie(
            labels=grouped[:11]['spc_common'],
            values=grouped[:11]['count'],
        )],
            layout=go.Layout(
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                font={
                    'color': colors['text2'],
                    'size': 14
                },
                title='Pie-chart of Tree Species by ' + title_part))
        piechart.update_traces(hoverinfo='label+value', textinfo='text+percent', opacity=0.9,
                               marker=dict(colors=px.colors.qualitative.Prism, line=dict(color='#000000', width=1)))

    if choiceRG != 'tree_speices':
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
    else:
        figure = piechart

    return figure


if __name__ == '__main__':

    app.run_server(debug=True)
