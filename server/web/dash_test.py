"""
Processes Collector Data with Plotly DASH dynamic plot.
"""
import time
import server.constants as consts
import dash
import threading
import sqlalchemy as sa
from sqlalchemy import desc
from dash.dependencies import Output, Input
from sqlalchemy.orm import Session
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from threading import Lock
from server.db.mappings import Update, DiskUpdate, GPUUpdate
import pandas as pd


def setup(host: str, port: int, user: str, password: str, dbname: str, verbose=False):
    """
    Sets up connection to DB
    :param host:
    :param port:
    :param user:
    :param password:
    :param dbname:
    :param verbose:
    :return:
    """
    # Create DB Session
    print("Connecting to Database...")
    engine = sa.create_engine(f"mysql://{user}:{password}@{host}:{port}/"
                              f"{dbname}", echo=verbose)
    session = Session(engine)
    return session

X = []
Y = []
node = 3
pool = 1
QLock = Lock()

app = dash.Dash(__name__)
app.title = "Shepherd Node Management"

server = app.server

app.layout = html.Div(
        [
                html.H1(f'Node {node} CPU Usage'),
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
    global X, Y
    with QLock:
        data = plotly.graph_objs.Scatter(
                x=list(X),
                y=list(Y),
                name='Scatter',
                mode='lines+markers',
                fill='tozeroy'
        )

        ret = {'data':   [data],
                'layout': go.Layout(xaxis=dict(range=[min(X) if len(X) > 0 else 0, max(X) if len(X) > 0 else 0]), yaxis=dict(range=[0, 110]), )}
    return ret


def db_work():
    global X, Y
    session = setup(consts.DB_URL, consts.DB_PORT, consts.DB_USER, consts.DB_PASSWORD, consts.DB_SCHEMA)
    while True:
        with QLock:
            query = session.query(Update).filter(Update.node_id == node).order_by(desc(Update.timestamp)).limit(10)
            updates = pd.read_sql(query.statement, query.session.bind)
            X = list(updates['timestamp'])[::-1]
            Y = list(updates['cpu_percent_usage'])[::-1]
        time.sleep(1)


if __name__ == "__main__":
    d = threading.Thread(target=app.run_server)
    d.start()
    db = threading.Thread(target=db_work)
    db.start()
