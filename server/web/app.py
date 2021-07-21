import os
import datetime as dt
import sqlalchemy as sa
import dash
import dash_core_components as dcc
import dash_html_components as dhtml

from dash.dependencies import Input, Output, State
from sqlalchemy.orm import Session
from server.db.mappings import HistoricalData, Node, Update, DiskUpdate, SessionUpdate, GPUUpdate, Pool

GRAPH_INT = os.environ.get("GRAPH_INT", 500)

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Shepherd Node Management"

server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = dhtml.Div(
    [
        # header
        dhtml.Div(
            [
                dhtml.Div(
                    [
                        dhtml.H4("Shepherd Node Manager", className="app__header__title"),
                        dhtml.P(
                            "This app updates with information pertaining to your nodes in real time.",
                            className="app__header__title--grey",
                        ),
                    ],
                    className="app__header__desc",
                ),
                dhtml.Div(
                    [
                        dhtml.A(
                            dhtml.Img(
                                src=app.get_asset_url("GitHub-Mark.png"),
                                className="app__menu__img",
                            ),
                            href="https://github.com/blackadar/shepherd",
                        ),
                    ],
                    className="app__header__logo",
                ),
            ],
            className="app__header",
        ),
        dhtml.Div(
            [
                dcc.Dropdown(
                    id='graph-dropdown',
                    options=[
                        {'label': 'CPU', 'value': 'CPU'},
                        {'label': 'RAM', 'value': 'RAM'},
                        {'label': 'GPU', 'value': 'GPU'},
                        {'label': 'Disk', 'value': 'disk'},
                        {'label': 'Battery', 'value': 'battery'}
                    ],
                    value='CPU',
                    clearable=False
                ),
            ],
            style={"width": "10%"}
        ),
        dhtml.Div(
            [
                # CPU
                dhtml.Div(
                    [
                        dhtml.Div(
                            [dhtml.H6("CPU", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="cpu-usage",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="cpu-usage-update",
                            interval=int(GRAPH_INT),
                            n_intervals=0,
                        ),
                    ],
                    hidden=False,
                    className="two-thirds column cpu_temp",
                    id="cpu-display"
                ),
                # RAM
                dhtml.Div(
                    [
                        dhtml.Div(
                            [dhtml.H6("RAM", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="ram-usage",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="ram-usage-update",
                            interval=int(GRAPH_INT),
                            n_intervals=0,
                        ),
                    ],
                    hidden=True,
                    className="two-thirds column ram_temp",
                    id="ram-display"

                ),
                # GPU
                dhtml.Div(
                    [
                        dhtml.Div(
                            [dhtml.H6("GPU", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="gpu-usage",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="gpu-usage-update",
                            interval=int(GRAPH_INT),
                            n_intervals=0,
                        ),
                    ],
                    hidden=True,
                    className="two-thirds column gpu_temp",
                    id="gpu-display"
                ),
                # Disk
                dhtml.Div(
                    [
                        dhtml.Div(
                            [dhtml.H6("Disk", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="disk-usage",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="disk-usage-update",
                            interval=int(GRAPH_INT),
                            n_intervals=0,
                        ),
                    ],
                    hidden=True,
                    className="two-thirds column disk_temp",
                    id="disk-display"
                ),
                # Battery
                dhtml.Div(
                    [
                        dhtml.Div(
                            [dhtml.H6("Battery", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="battery-usage",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="battery-usage-update",
                            interval=int(GRAPH_INT),
                            n_intervals=0,
                        ),
                    ],
                    hidden=True,
                    className="two-thirds column battery_temp",
                    id="battery-display"
                ),
                dhtml.Div(
                    [
                        # histogram
                        dhtml.Div(
                            [
                                dhtml.Div(
                                    [
                                        dhtml.H6(
                                            "WIND SPEED HISTOGRAM",
                                            className="graph__title",
                                        )
                                    ]
                                ),
                                dhtml.Div(
                                    [
                                        dcc.Slider(
                                            id="bin-slider",
                                            min=1,
                                            max=60,
                                            step=1,
                                            value=20,
                                            updatemode="drag",
                                            marks={
                                                20: {"label": "20"},
                                                40: {"label": "40"},
                                                60: {"label": "60"},
                                            },
                                        )
                                    ],
                                    className="slider",
                                ),
                                dhtml.Div(
                                    [
                                        dcc.Checklist(
                                            id="bin-auto",
                                            options=[
                                                {"label": "Auto", "value": "Auto"}
                                            ],
                                            value=["Auto"],
                                            inputClassName="auto__checkbox",
                                            labelClassName="auto__label",
                                        ),
                                        dhtml.P(
                                            "# of Bins: Auto",
                                            id="bin-size",
                                            className="auto__p",
                                        ),
                                    ],
                                    className="auto__container",
                                ),
                                dcc.Graph(
                                    id="wind-histogram",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            hidden=True,
                            className="graph__container first",
                        ),
                        # wind direction
                        dhtml.Div(
                            [
                                dhtml.Div(
                                    [
                                        dhtml.H6(
                                            "WIND DIRECTION", className="graph__title"
                                        )
                                    ]
                                ),
                                dcc.Graph(
                                    id="wind-direction",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            hidden=True,
                            className="graph__container second",
                        ),
                    ],
                    className="one-third column histogram__direction",
                ),
            ],
            className="app__content",
        ),
    ],
    className="app__container",
)


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


def get_current_time():
    """ Helper function to get the current time in seconds. """

    now = dt.datetime.now()
    total_time = (now.hour * 3600) + (now.minute * 60) + (now.second)
    return total_time


def update():
    return


#@app.callback(
#    Output("cpu-usage", "figure"), [Input("cpu-usage-update", "n_intervals")]
#)
#def gen_cpu_usage(interval):
#    """
#    Generate the wind speed graph.
#    :params interval: update the graph based on an interval
#    """
#
#    total_time = get_current_time()
#    df = get_wind_data(total_time - 200, total_time)
#
#    trace = dict(
#        type="scatter",
#        y=df["Speed"],
#        line={"color": "#42C4F7"},
#        hoverinfo="skip",
#        error_y={
#            "type": "data",
#            "array": df["SpeedError"],
#            "thickness": 1.5,
#            "width": 2,
#            "color": "#B4E8FC",
#        },
#        mode="lines",
#    )
#
#    layout = dict(
#        plot_bgcolor=app_color["graph_bg"],
#        paper_bgcolor=app_color["graph_bg"],
#        font={"color": "#fff"},
#        height=700,
#        xaxis={
#            "range": [0, 200],
#            "showline": True,
#            "zeroline": False,
#            "fixedrange": True,
#            "tickvals": [0, 50, 100, 150, 200],
#            "ticktext": ["200", "150", "100", "50", "0"],
#            "title": "Time Elapsed (sec)",
#        },
#        yaxis={
#            "range": [
#                min(0, min(df["Speed"])),
#                max(45, max(df["Speed"]) + max(df["SpeedError"])),
#            ],
#            "showgrid": True,
#            "showline": True,
#            "fixedrange": True,
#            "zeroline": False,
#            "gridcolor": app_color["graph_line"],
#            "nticks": max(6, round(df["Speed"].iloc[-1] / 10)),
#        },
#    )
#
#    return dict(data=[trace], layout=layout)

def main():
    session = setup('64.227.2.44', 3306, 'shepherd', 'Tcg3Dvq2', 'shepherd')

if __name__ == "__main__":
    app.run_server(debug=True)
