import server.constants as const
import dash
from server.web.connector import ShepherdConnection
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], update_title=None)
app.title = "Shepherd"
server = app.server
connection = ShepherdConnection(const.DB_URL, const.DB_PORT, const.DB_USER, const.DB_PASSWORD, const.DB_SCHEMA)
