import datetime

import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from server.web.app import app, connection
from server.web.connector import format_disks, format_nodes, format_gpus


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
    updates = connection.get_combined_updates(node, gpu_uuid, disk_id, num_updates, no_gpu=(gpu_uuid == ''),
                                              no_disks=(disk_id == ''))
    x = list(updates['timestamp'])[::-1]

    if len(updates) == 0:
        x = [datetime.datetime.now(), ]

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

    swap_y = list(updates['ram_percent_swap'])[::-1]
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
            value=updates['cpu_current_frequency'].iloc[0] if len(updates) > 0 else 0,
            title={'text': 'CPU Frequency'},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                    'axis':        {'range':     [None,
                                                  updates['cpu_max_frequency'].iloc[-1] if len(updates) > 0 else 0]
                            , 'tickwidth':       1,
                                    'tickcolor': "darkblue"},
                    'bar':         {'color': "darkblue"},
                    'bgcolor':     "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
            }
    ))

    cpu_1_graph = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=updates['cpu_load_1'].iloc[0] * 100 if len(updates) > 0 else 0,
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
            delta={'reference': updates['cpu_load_1'].iloc[-1] * 100 if len(updates) > 0 else 0}
    ))

    cpu_5_graph = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=updates['cpu_load_5'].iloc[0] * 100 if len(updates) > 0 else 0,
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
            delta={'reference': updates['cpu_load_5'].iloc[-1] * 100 if len(updates) > 0 else 0}
    ))

    cpu_15_graph = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=updates['cpu_load_15'].iloc[0] * 100 if len(updates) > 0 else 0,
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
            delta={'reference': updates['cpu_load_15'].iloc[-1] * 100 if len(updates) > 0 else 0}
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


@app.callback(
        Output('hist-node-dropdown', 'options'),
        [Input('hist-node-dropdown', 'value')]
)
def update_telemetry_node_dropdown(name):
    return format_nodes(connection)


@app.callback(
        Output('hist-cpu-graph', 'figure'),
        Output('hist-vram-graph', 'figure'),
        Output('hist-swap-graph', 'figure'),
        Output('hist-disk-graph', 'figure'),
        Output('hist-gpu-graph', 'figure'),
        [Input('hist-graph-update', 'n_intervals'),
         Input('hist-node-dropdown', 'value')]
)
def update_historical_graphs(n_intervals, node):
    df = connection.get_historical(node)
    x = list(df['time'])[::-1]

    if len(df) == 0:
        x = [datetime.datetime.now(), ]

    cpu_y = list(df['avg_cpu_percent_usage'])[::-1]
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
                         title='Average CPU Utilization',
                 )}

    ram_y = list(df['avg_ram_used_virt'] / (1000 * 1000 * 1000))[::-1]
    if len(ram_y) == 0:
        ram_y = [0, ]
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
                         yaxis=dict(range=[0, max(ram_y) + 25]),
                         title='Average Virtual RAM Usage',
                 )}

    swap_y = list(df['avg_ram_used_swap'] / (1000 * 1000 * 1000))[::-1]
    if len(swap_y) == 0:
        swap_y = [0, ]
    swap_data = plotly.graph_objs.Scatter(
            x=x,
            y=swap_y,
            name='Scatter',
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='pink', width=0.75),
    )
    swap_graph = {'data':   [swap_data],
                  'layout': go.Layout(
                          xaxis=dict(range=[min(x), max(x)]),
                          yaxis=dict(range=[0, max(swap_y) + 25]),
                          title='Average Swap Space',
                  )}

    disk_y = list(df['total_disk_used'] / (1000 * 1000 * 1000))[::-1]
    if len(disk_y) == 0:
        disk_y = [0, ]
    disk_data = plotly.graph_objs.Scatter(
            x=x,
            y=disk_y,
            name='Scatter',
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='plum', width=0.75),
    )
    disk_graph = {'data':   [disk_data],
                  'layout': go.Layout(
                          xaxis=dict(range=[min(x), max(x)]),
                          yaxis=dict(range=[0, max(disk_y) + 25]),
                          title='Average Disk Usage',
                  )}

    gpu_y = list(df['avg_gpu_load'] * 100)[::-1]
    gpu_data = plotly.graph_objs.Scatter(
            x=x,
            y=gpu_y,
            name='Scatter',
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='salmon', width=0.75),
    )
    gpu_graph = {'data':   [gpu_data],
                 'layout': go.Layout(
                         xaxis=dict(range=[min(x), max(x)]),
                         yaxis=dict(range=[0, 110]),
                         title='Average GPU Load',
                 )}

    return cpu_graph, ram_graph, swap_graph, disk_graph, gpu_graph


@app.callback(
        Output('anomaly-space', 'children'),
        [Input('anomaly-update', 'n_intervals')]
)
def update_anomalies(n):
    unresolved = connection.get_unresolved_anomalies()
    resolved = connection.get_resolved_anomalies()
    children = []

    children.append(html.H1("Unresolved"))
    for idx, row in unresolved.iterrows():
        if row['severity'] == 'high':
            color = 'danger'
        elif row['severity'] == 'medium':
            color = 'warning'
        else:
            color = 'info'
        children.append(dbc.Alert(f"{(row['name']) if row['name'].lower() != 'node' else ('Node ' + str(row['node_id']))} has an unresolved {row['type']} anomaly: "
                                  f"{row['message']} ({row['time']})", color=color))

    children.append(html.Br())
    children.append(html.H1("Resolved"))
    for idx, row in resolved.iterrows():
        children.append(dbc.Alert(f"{(row['name']) if row['name'].lower() != 'node' else ('Node ' + str(row['node_id']))} had a {row['type']} anomaly: "
                                  f"{row['message']} ({row['time']})", color='dark'))
    children.append(html.Br())
    return html.Div(children)

@app.callback(
        Output('overview-space', 'children'),
        [Input('overview-update', 'n_intervals')]
)
def update_overview(n):
    pairs = connection.get_node_name_pairs()
    children = []

    for node_id, node_name in pairs:
        updates = connection.get_updates(node_id, 1)
        anomalies = connection.get_num_unresolved_anomalies_node(node_id)
        fill_2 = f'{anomalies} outstanding anomal' + ('y' if anomalies == 1 else 'ies')
        if len(updates) > 0:
            update = updates.iloc[0]
            timestamp = update['timestamp']
            cores = update['cpu_logical_cores']
            frequency = update['cpu_max_frequency']
            ram = update['ram_total_virtual']
            uptime = update['session_uptime']
            lead = f'Last Reported {timestamp}'
            fill = f'{cores} cores @ {frequency/1000: 0.2f} GHz, ' \
                   f'{ram / 1024 / 1000000: 0.1f} GB RAM, ' \
                   f'{uptime / 60 / 60 : 0.2f} hours uptime'
        else:
            lead = "No recent updates."
            fill = "This node appears to have stopped reporting."
        children.append(html.Br())
        children.append(dbc.Jumbotron([
                html.H1(f"{node_name}{(' ' + str(node_id)) if (node_name.lower() == 'node') else ''}", className="display-3"),
                html.P(
                        f"{lead}",
                        className="lead",
                ),
                html.Hr(className="my-2"),
                html.P(
                        f"{fill}",
                ),
                html.P(
                        f"{fill_2}",
                )
        ]))

    return html.Div(children)

@app.callback(
        Output('node-badge', 'children'),
        Output('anomaly-badge', 'children'),
        [Input('deck-update', 'n_intervals')]
)
def update_home_badges(n):
    nodes = connection.get_num_nodes()
    anomalies = connection.get_num_unresolved_anomalies()
    return nodes, anomalies
