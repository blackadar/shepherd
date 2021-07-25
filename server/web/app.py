import server.constants as const
import dash
import threading
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from server.web.connector import ShepherdConnection
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Shepherd"
server = app.server
connection = ShepherdConnection(const.DB_URL, const.DB_PORT, const.DB_USER, const.DB_PASSWORD, const.DB_SCHEMA)


def format_nodes():
    """
    Returns Nodes formatted in Dash friendly manner.
    :return: list of Dicts
    """
    nodes = connection.get_nodes()
    res = []
    for node in nodes:
        res.append({'label': f'Node {node}', 'value': node})
    return res


navbar = dbc.NavbarSimple(
        children=[
                dbc.NavItem(dbc.NavLink("Page 1", href="#")),
                dbc.DropdownMenu(
                        children=[
                                dbc.DropdownMenuItem("More pages", header=True),
                                dbc.DropdownMenuItem("Page 2", href="#"),
                                dbc.DropdownMenuItem("Page 3", href="#"),
                        ],
                        nav=True,
                        in_navbar=True,
                        label="More",
                ),
        ],
        brand="Shepherd",
        brand_href="#",
        brand_style={'align': 'left'},
        color="dark",
        dark=True,
)

app.layout = html.Div(
        [
                navbar,
                html.Div([
                        html.Div([
                                html.H1(f'Node Telemetry', id='title', style={'textAlign': 'center'}),
                                html.Br(),
                                dcc.Dropdown(
                                        id='node-dropdown',
                                        options=format_nodes(),
                                        value=connection.get_nodes()[0]),
                                html.Br(),
                                html.Div([
                                        dcc.Slider(
                                                id='sample-slider',
                                                min=10,
                                                max=310,
                                                value=10,
                                                step=50,
                                                marks={str(i): str(i - 10) for i in range(10, 310, 50)}),
                                ])])
                ], style={'width': '66%', 'padding-left': '33%', 'padding-right': '1%'}),
                html.Div([
                        html.Div([
                                dcc.Graph(
                                        id='top-graph1'
                                ),
                        ], style={'width': '25%', 'display': 'inline-block'}),
                        html.Div([
                                dcc.Graph(
                                        id='top-graph2'
                                ),
                        ], style={'width': '25%', 'display': 'inline-block'}),
                        html.Div([
                                dcc.Graph(
                                        id='top-graph3'
                                ),
                        ], style={'width': '25%', 'display': 'inline-block'}),
                        html.Div([
                                dcc.Graph(
                                        id='top-graph4'
                                ),
                        ], style={'width': '25%', 'display': 'inline-block'}),
                ]),
                html.Br(),
                dcc.Graph(id='cpu-graph', animate=True),
                dcc.Graph(id='vram-graph', animate=True),
                dcc.Graph(id='swap-graph', animate=True),
                dcc.Interval(
                        id='graph-update',
                        interval=1000,
                        n_intervals=0),
        ])


@app.callback(
        Output('cpu-graph', 'figure'),
        Output('vram-graph', 'figure'),
        Output('swap-graph', 'figure'),
        Output('top-graph1', 'figure'),
        Output('top-graph2', 'figure'),
        Output('top-graph3', 'figure'),
        Output('top-graph4', 'figure'),
        [Input('graph-update', 'n_intervals'),
         Input('sample-slider', 'value'),
         Input('node-dropdown', 'value')]
)
def update_graphs(n_intervals, num_updates, node):
    df = connection.get_updates(node, num_updates)
    x = list(df['timestamp'])[::-1]

    cpu_y = list(df['cpu_percent_usage'])[::-1]
    cpu_data = plotly.graph_objs.Scatter(
            x=x,
            y=cpu_y,
            name='Scatter',
            mode='lines+markers',
            fill='tozeroy',
            line=dict(width=0.75, color='lightblue'),
    )
    cpu_graph = {'data':   [cpu_data],
                 'layout': go.Layout(
                         xaxis=dict(range=[min(x), max(x)]),
                         yaxis=dict(range=[0, 110]),
                         title='CPU Utilization',
                 )}

    ram_y = list(df['ram_used_virtual'] / df['ram_total_virtual'] * 100)[::-1]
    ram_data = plotly.graph_objs.Scatter(
            x=x,
            y=ram_y,
            name='Scatter',
            mode='lines+markers',
            fill='tozeroy',
            line=dict(width=0.75, color='lavender'),
    )
    ram_graph = {'data':   [ram_data],
                 'layout': go.Layout(
                         xaxis=dict(range=[min(x), max(x)]),
                         yaxis=dict(range=[0, 110]),
                         title='Virtual RAM',
                 )}

    swap_y = list(df['ram_percent_swap'] * 100)[::-1]
    swap_data = plotly.graph_objs.Scatter(
            x=x,
            y=swap_y,
            name='Scatter',
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='lavenderblush', width=0.75),
    )
    swap_graph = {'data':   [swap_data],
                  'layout': go.Layout(
                          xaxis=dict(range=[min(x), max(x)]),
                          yaxis=dict(range=[0, 110]),
                          title='Swap Space',
                  )}

    cpu_freq_graph = go.Figure(go.Indicator(
            mode='gauge+number',
            value=df['cpu_current_frequency'].iloc[0],
            title={'text': 'CPU Frequency'},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                    'axis':        {'range':     [None, df['cpu_max_frequency'].iloc[-1]], 'tickwidth': 1,
                                    'tickcolor': "darkblue"},
                    'bar':         {'color': "darkblue"},
                    'bgcolor':     "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
            }
    ))

    cpu_1_graph = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=df['cpu_load_1'].iloc[0] * 100,
            number={'suffix': "%"},
            title={'text': '1m Load'},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                    'axis':        {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar':         {'color': "darkblue"},
                    'bgcolor':     "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
            },
            delta={'reference': df['cpu_load_1'].iloc[-1] * 100}
    ))

    cpu_5_graph = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=df['cpu_load_5'].iloc[0] * 100,
            number={'suffix': "%"},
            title={'text': '5m Load'},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                    'axis':        {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar':         {'color': "darkblue"},
                    'bgcolor':     "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
            },
            delta={'reference': df['cpu_load_5'].iloc[-1] * 100}
    ))

    cpu_15_graph = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=df['cpu_load_15'].iloc[0] * 100,
            number={'suffix': "%"},
            title={'text': '15m Load'},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                    'axis':        {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar':         {'color': "darkblue"},
                    'bgcolor':     "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
            },
            delta={'reference': df['cpu_load_15'].iloc[-1] * 100}
    ))
    return cpu_graph, ram_graph, swap_graph, cpu_freq_graph, cpu_1_graph, cpu_5_graph, cpu_15_graph


@app.callback(
        dash.dependencies.Output('node-dropdown', 'options'),
        [dash.dependencies.Input('node-dropdown', 'value')]
)
def update_date_dropdown(name):
    return format_nodes()


if __name__ == "__main__":
    d = threading.Thread(target=app.run_server)
    d.start()
