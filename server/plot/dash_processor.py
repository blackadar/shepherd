"""
Processes Collector Data with Plotly DASH dynamic plot.
"""
from server.processor import Processor
import dash
import threading
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from collections import deque
from threading import Lock


class DashProcessor(Processor):
    """
    Dynamic Dash plots from Updates.
    """

    def __init__(self):
        super().__init__()
        self._x = 2
        self.X = deque(maxlen=10)
        self.X.append(1)
        self.Y = deque(maxlen=10)
        self.Y.append(1)
        self.QLock = Lock()
        self.dash()


    def dash(self):
        app = dash.Dash(__name__)
        app.layout = html.Div(
                [
                        html.H1('CPU Usage'),
                        dcc.Graph(id='live-graph', animate=True),
                        dcc.Interval(
                                id='graph-update',
                                interval=1000,
                                n_intervals=0
                        ),
                ]
        )

        @app.callback(
                Output('live-graph', 'figure'),
                [Input('graph-update', 'n_intervals')]
        )
        def update_graph_scatter(n):
            with self.QLock:
                data = plotly.graph_objs.Scatter(
                        x=list(self.X),
                        y=list(self.Y),
                        name='Scatter',
                        mode='lines+markers',
                )

                ret = {'data':   [data],
                        'layout': go.Layout(xaxis=dict(range=[min(self.X), max(self.X)]), yaxis=dict(range=[0, 100]), )}
            return ret
        thread = threading.Thread(target=app.run_server)
        thread.start()

    def processor_name(self) -> str:
        return "dash"

    def update(self, pool_id: int, node_id: int, update: dict) -> None:
        with self.QLock:
            self.X.append(self._x)
            self.Y.append(update['cpu']['percent'])
            self._x += 1

