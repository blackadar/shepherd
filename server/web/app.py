import datetime

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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], update_title=None)
app.title = "Shepherd"
server = app.server
connection = ShepherdConnection(const.DB_URL, const.DB_PORT, const.DB_USER, const.DB_PASSWORD, const.DB_SCHEMA)
df_nodes = connection.get_nodes()
default_node = df_nodes[0] if len(df_nodes) > 0 else 0
df_gpus = connection.get_gpus(default_node)
default_gpu = df_gpus[0] if len(df_gpus) > 0 else 0
df_disks = connection.get_disks(default_node)
default_disk = df_disks[0] if len(df_disks) > 0 else 0


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


def format_gpus(node_id: int):
    """
    Returns GPUs formatted in Dash friendly manner.
    :return: list of Dicts
    """
    gpus = connection.get_gpus(node_id)
    res = []
    for gpu in gpus:
        res.append({'label': f'{gpu}', 'value': gpu})
    return res


def format_disks(node_id: int):
    """
    Returns Nodes formatted in Dash friendly manner.
    :return: list of Dicts
    """
    disks = connection.get_disks(node_id)
    res = []
    for disk in disks:
        res.append({'label': f'{disk}', 'value': disk})
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
                html.Br(),
                html.Div([
                        html.Div([
                                html.H1(f'Node Telemetry', id='title', style={'textAlign': 'center'}),
                                html.Br(),
                                dcc.Dropdown(
                                        id='node-dropdown',
                                        searchable=False,
                                        options=format_nodes(),
                                        value=default_node),
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
                html.Div([
                        dcc.Dropdown(
                                id='gpu-dropdown',
                                options=format_gpus(connection.get_nodes()[0]),
                                value=default_gpu,
                        )
                ], style={'width': '66%', 'padding-left': '33%', 'padding-right': '1%'}),
                dcc.Graph(id='gpu-graph', animate=True),
                html.Div([
                        dcc.Dropdown(
                                id='disk-dropdown',
                                options=format_disks(connection.get_nodes()[0]),
                                value=default_disk,
                        )
                ], style={'width': '66%', 'padding-left': '33%', 'padding-right': '1%'}),
                dcc.Graph(id='disk-graph', animate=True),
                dcc.Interval(
                        id='graph-update',
                        interval=1000,
                        n_intervals=0),
        ])


@app.callback(
        Output('cpu-graph', 'figure'),
        Output('vram-graph', 'figure'),
        Output('swap-graph', 'figure'),
        Output('gpu-graph', 'figure'),
        Output('disk-graph', 'figure'),
        Output('top-graph1', 'figure'),
        Output('top-graph2', 'figure'),
        Output('top-graph3', 'figure'),
        Output('top-graph4', 'figure'),
        [Input('graph-update', 'n_intervals'),
         Input('sample-slider', 'value'),
         Input('node-dropdown', 'value'),
         Input('gpu-dropdown', 'value'),
         Input('disk-dropdown', 'value')]
)
def update_graphs(n_intervals, num_updates, node, gpu_uuid, disk_id):
    updates = connection.get_combined_updates(node, gpu_uuid, disk_id, num_updates, no_gpu=(gpu_uuid == ''), no_disks=(disk_id == ''))
    x = list(updates['timestamp'])[::-1]

    if len(x) == 0:
        x = [datetime.datetime.now(),]

    cpu_y = list(updates['cpu_percent_usage'])[::-1]
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
                         yaxis=dict(range=[0, 101]),
                         title='CPU Utilization',
                 )}

    ram_y = list(updates['ram_used_virtual'] / updates['ram_total_virtual'] * 100)[::-1]
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
                         yaxis=dict(range=[0, 101]),
                         title='Virtual RAM',
                 )}

    swap_y = list(updates['ram_percent_swap'] * 100)[::-1]
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
                          yaxis=dict(range=[0, 101]),
                          title='Swap Space',
                  )}
    if 'load' in updates.keys():
        gpu_y = list(updates['load'] * 100)[::-1]
    else:
        gpu_y = []
    gpu_data = plotly.graph_objs.Scatter(
            x=x,
            y=gpu_y,
            name='Scatter',
            mode='lines+markers',
            fill='tozeroy',
            line=dict(width=0.75, color='lightgreen'),
    )
    gpu_graph = {'data':   [gpu_data],
                 'layout': go.Layout(
                         xaxis=dict(range=[min(x), max(x)]),
                         yaxis=dict(range=[0, 101]),
                         title='GPU Utilization',
                 )}

    if 'percentage_used' in updates.keys():
        disk_y = list(updates['percentage_used'])[::-1]
    else:
        disk_y = []
    disk_data = plotly.graph_objs.Scatter(
            x=x,
            y=disk_y,
            name='Scatter',
            mode='lines+markers',
            fill='tozeroy',
            line=dict(width=0.75, color='papayawhip'),
    )
    disk_graph = {'data':   [disk_data],
                 'layout': go.Layout(
                         xaxis=dict(range=[min(x), max(x)]),
                         yaxis=dict(range=[0, 101]),
                         title='Disk Utilization',
                 )}

    cpu_freq_graph = go.Figure(go.Indicator(
            mode='gauge+number',
            value=updates['cpu_current_frequency'].iloc[0],
            title={'text': 'CPU Frequency'},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                    'axis':        {'range':     [None, updates['cpu_max_frequency'].iloc[-1]], 'tickwidth': 1,
                                    'tickcolor': "darkblue"},
                    'bar':         {'color': "darkblue"},
                    'bgcolor':     "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
            }
    ))

    cpu_1_graph = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=updates['cpu_load_1'].iloc[0] * 100,
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
            delta={'reference': updates['cpu_load_1'].iloc[-1] * 100}
    ))

    cpu_5_graph = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=updates['cpu_load_5'].iloc[0] * 100,
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
            delta={'reference': updates['cpu_load_5'].iloc[-1] * 100}
    ))

    cpu_15_graph = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=updates['cpu_load_15'].iloc[0] * 100,
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
            delta={'reference': updates['cpu_load_15'].iloc[-1] * 100}
    ))
    return cpu_graph, ram_graph, swap_graph, gpu_graph, disk_graph, cpu_freq_graph, cpu_1_graph, cpu_5_graph, cpu_15_graph


@app.callback(
        Output('node-dropdown', 'options'),
        [Input('node-dropdown', 'value')]
)
def update_node_dropdown(name):
    return format_nodes()

@app.callback(
        Output('gpu-dropdown', 'options'),
        Output('gpu-dropdown', 'value'),
        [Input('node-dropdown', 'value')]
)
def update_gpu_dropdown(node):
    fmt = format_gpus(node)
    if len(fmt) > 0:
        return fmt, fmt[0]['value']
    else:
        return [], ''

@app.callback(
        Output('disk-dropdown', 'options'),
        Output('disk-dropdown', 'value'),
        [Input('node-dropdown', 'value')]
)
def update_disk_dropdown(node):
    fmt = format_disks(node)
    if len(fmt) > 0:
        return fmt, fmt[0]['value']
    else:
        return [], ''


if __name__ == "__main__":
    d = threading.Thread(target=app.run_server)
    d.start()
