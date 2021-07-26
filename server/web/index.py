import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import server.constants as const
from app import app
from layouts import telemetry, home, historical
import callbacks

app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/telemetry':
        return telemetry
    elif pathname == '/historical':
        return historical
    elif pathname == '/anomaly':
        return '500'
    elif pathname == '/':
        return home
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=const.WEB_DEBUG)
