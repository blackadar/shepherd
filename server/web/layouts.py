import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import server.constants as const
from server.web.app import connection
from server.web.connector import format_gpus, format_disks, format_nodes

df_nodes = connection.get_nodes()
default_node = df_nodes[0] if len(df_nodes) > 0 else 0
df_gpus = connection.get_gpus(default_node)
default_gpu = df_gpus[0] if len(df_gpus) > 0 else 0
df_disks = connection.get_disks(default_node)
default_disk = df_disks[0] if len(df_disks) > 0 else 0

navbar = dbc.NavbarSimple(
        children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.DropdownMenu(
                        children=[
                                dbc.DropdownMenuItem("Services", header=True),
                                dbc.DropdownMenuItem("Telemetry", href="/telemetry"),
                                dbc.DropdownMenuItem("Historical", href="/historical"),
                                dbc.DropdownMenuItem("Anomaly", href="/anomaly"),
                        ],
                        nav=True,
                        in_navbar=True,
                        label="More",
                ),
        ],
        brand="Shepherd",
        brand_href="/",
        brand_style={'align': 'left'},
        color="dark",
        dark=True,
)

nav_deck = html.Div([dbc.CardDeck(
        [
                dbc.Card(
                        dbc.CardBody(
                                [
                                        html.H5(["Node Telemetry", dbc.Badge("x", id="node-badge", className="ml-1")],
                                                className="card-title"),
                                        html.P(
                                                "View live updating plots and figures "
                                                "for each Node in your network.",
                                                className="card-text",
                                        ),
                                        dbc.Button(
                                                "Telemetry", color="success", className="mt-auto", href='/telemetry'
                                        ),
                                ]
                        )
                ),
                dbc.Card(
                        dbc.CardBody(
                                [
                                        html.H5(["Historical Data"], className="card-title"),
                                        html.P(
                                                "Navigate plots and figures from condensed "
                                                "performance data over time.",
                                                className="card-text",
                                        ),
                                        dbc.Button(
                                                "Historical Data", color="warning", className="mt-auto",
                                                href='/historical'
                                        ),
                                ]
                        )
                ),
                dbc.Card(
                        dbc.CardBody(
                                [
                                        html.H5(["Anomalies",
                                                 dbc.Badge("", color='danger', id="anomaly-badge", className="ml-1")],
                                                className="card-title"),
                                        html.P(
                                                "See past and present anomalous metrics "
                                                "from systems on the network.",
                                                className="card-text",
                                        ),
                                        dbc.Button(
                                                "Anomalies", color="danger", className="mt-auto", href='/anomaly'
                                        ),
                                ]
                        )
                ),
        ]
), dcc.Interval(
        id='deck-update',
        interval=1000,
        n_intervals=0)
])

home = html.Div([
        navbar,
        dbc.Container([
                dbc.Row([
                        html.H1(f'Shepherd @ {const.WEB_LOCATION}',
                                style={'textAlign': 'center'}),
                        html.Br(),
                        nav_deck],
                        justify="center",
                        align="center",
                        className="h-50")],
                style={"height": "100vh"})
])

telemetry = html.Div(
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
                                        options=format_nodes(connection),
                                        value=default_node),
                                html.Br(),
                                html.Div([
                                        dcc.Slider(
                                                id='sample-slider',
                                                min=10,
                                                max=310,
                                                value=100,
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
                                options=format_gpus(connection, default_node),
                                value=default_gpu,
                        )
                ], style={'width': '66%', 'padding-left': '33%', 'padding-right': '1%'}),
                dcc.Graph(id='gpu-graph', animate=True),
                html.Div([
                        dcc.Dropdown(
                                id='disk-dropdown',
                                options=format_disks(connection, default_node),
                                value=default_disk,
                        )
                ], style={'width': '66%', 'padding-left': '33%', 'padding-right': '1%'}),
                dcc.Graph(id='disk-graph', animate=True),
                dcc.Interval(
                        id='graph-update',
                        interval=1000,
                        n_intervals=0),
        ])

historical = html.Div(
        [
                navbar,
                html.Div([
                        html.Div([
                                html.Br(),
                                html.H1(f'Historical Data', id='title', style={'textAlign': 'center'}),
                                html.Br(),
                                dcc.Dropdown(
                                        id='hist-node-dropdown',
                                        searchable=False,
                                        options=format_nodes(connection),
                                        value=default_node),
                                html.Br(),
                        ])
                ], style={'width': '66%', 'padding-left': '33%', 'padding-right': '1%'}),
                html.Br(),
                dcc.Graph(id='hist-cpu-graph', animate=True),
                dcc.Graph(id='hist-vram-graph', animate=True),
                dcc.Graph(id='hist-swap-graph', animate=True),
                dcc.Graph(id='hist-disk-graph', animate=True),
                dcc.Graph(id='hist-gpu-graph', animate=True),
                dcc.Interval(
                        id='hist-graph-update',
                        disabled=False,
                        interval=1000 * 60 * 60 * 48,  # Updates every 2 days
                        n_intervals=0),
        ])

anomaly = html.Div([
        navbar,
        html.Br(),
        html.Div(id='anomaly-space', style={'width': '95%', 'margin': 25}),
        dcc.Interval(
                id='anomaly-update',
                interval=1000,
                n_intervals=0)
])
