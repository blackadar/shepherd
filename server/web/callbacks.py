from dash.dependencies import Input, Output
from app import app
import plotly
import plotly.graph_objs as go
import datetime
from app import connection
from connector import format_disks, format_nodes, format_gpus


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
def update_telemetry_graphs(n_intervals, num_updates, node, gpu_uuid, disk_id):
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
def update_telemetry_node_dropdown(name):
    return format_nodes(connection)


@app.callback(
        Output('gpu-dropdown', 'options'),
        Output('gpu-dropdown', 'value'),
        [Input('node-dropdown', 'value')]
)
def update_telemetry_gpu_dropdown(node):
    fmt = format_gpus(connection, node)
    if len(fmt) > 0:
        return fmt, fmt[0]['value']
    else:
        return [], ''


@app.callback(
        Output('disk-dropdown', 'options'),
        Output('disk-dropdown', 'value'),
        [Input('node-dropdown', 'value')]
)
def update_telemetry_disk_dropdown(node):
    fmt = format_disks(connection, node)
    if len(fmt) > 0:
        return fmt, fmt[0]['value']
    else:
        return [], ''
