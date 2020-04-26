import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

token = 'pk.eyJ1IjoibWlzaGtpY2UiLCJhIjoiY2s5MG94bWRoMDQxdjNmcHI1aWI1YnFkYyJ9.eFsHqEMYY7qxa0Pb9USCtQ'

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
        accesstoken=token,
        style="mapbox://styles/mishkice/ck98qopeo05k21ipc1atfdn8h",
        center=dict(
            lon=-73.91251,
            lat=40.7342
        ),
        zoom=10,
    ))


def gen_map():
    # groupby returns a dictionary mapping the values of the first field
    # 'classification' onto a list of record dictionaries with that
    # classification value.
    return {
        "data": [{
            "type": "scattermapbox",
            "lat": 40.7342,
            "lon": -73.91251,
        }],
        "layout": layout_map
    }


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
                    figure=gen_map()
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
