import logging
import os

import dash
import dash_bootstrap_components as dbc
from dash import Dash, Output, Input, dcc
from dash import html

from util import get_authz

external_stylesheets = [dbc.themes.SKETCHY]

logger = logging.getLogger('dash')

print('DASH_URL_BASE_PATHNAME', os.environ.get('DASH_URL_BASE_PATHNAME', default="~not set~"))
app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)


@app.server.before_request
def check_privileges():
    """Do this before every call"""
    get_authz()


# Clientside callback: refresh token by calling fence's /user endpoint
app.clientside_callback(
    """
    // Call fence's /user endpoint, parse the response and update the profile 
    async function(n_intervals, data) {
        const response = await fetch(location.origin + '/user/user');
        if (!response.ok) {
            console.log('error retrieving user', response )
            return 'Profile (unauthorized)';
        } else {
            const user = await response.json();
            console.log('clientside_callback you are logged in as:', user.username);
            return 'Profile (' + user.username + ')';
        }        
    }
    """,
    Output('nav_item-profile', 'children'),
    Input('clientside-interval', 'n_intervals')
)


app.layout = dbc.Container([
    html.H1("ACED", className="display-3"),
    html.P(
        "A simple dash app.",
        className="lead",
    ),

    dbc.Nav(
        [
            dbc.NavItem(
                dbc.NavLink(f"{page['name']}", href=page["relative_path"], id=f'nav_item-{page["name"].lower()}')
            )
            for page in dash.page_registry.values()
        ]
    ),

    html.Hr(className="my-2"),
    # define a timed client side action here
    dcc.Interval(
        id='clientside-interval',
        n_intervals=0,
        interval=60 * 1000  # in milliseconds check every minute
    ),
    # other page contents goes here
    dash.page_container
])


if __name__ == '__main__':
    app.run_server(host="0.0.0.0",  debug=True)  #
