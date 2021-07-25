import server.constants as const
import dash
import threading
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from server.web.connector import ShepherdConnection

app = dash.Dash(__name__)
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


app.layout = html.Div(
        [
                html.H1(f'Node Telemetry', id='title'),
                html.Div([
                          dcc.Dropdown(
                                id='node-dropdown',
                                options=format_nodes(),
                                value=connection.get_nodes()[0]),
                          dcc.Slider(
                                id='sample-slider',
                                min=10,
                                max=100,
                                value=10,
                                step=1
                          )]),
                html.H4('CPU'),
                dcc.Graph(id='cpu-graph', animate=True),
                html.H4('RAM'),
                dcc.Graph(id='ram-graph', animate=True),
                dcc.Interval(
                        id='graph-update',
                        interval=1000,
                        n_intervals=0
                ),
        ]
)


@app.callback(
        Output('cpu-graph', 'figure'),
        Output('ram-graph', 'figure'),
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
            fill='tozeroy'
    )
    cpu_graph = {'data':   [cpu_data],
                 'layout': go.Layout(xaxis=dict(range=[min(x), max(x)]), yaxis=dict(range=[0, 110]), )}

    ram_y = list(df['ram_used_virtual'] / df['ram_total_virtual'] * 100)[::-1]
    ram_data = plotly.graph_objs.Scatter(
            x=x,
            y=ram_y,
            name='Scatter',
            mode='lines+markers',
            fill='tozeroy'
    )
    ram_graph = {'data':   [ram_data],
                 'layout': go.Layout(xaxis=dict(range=[min(x), max(x)]), yaxis=dict(range=[0, 110]), )}

    return cpu_graph, ram_graph


if __name__ == "__main__":
    d = threading.Thread(target=app.run_server)
    d.start()
