
import logging

import dash
from dash import html, dash_table, dcc

from figures.project import counts as project_counts

logger = logging.getLogger('dash')


dash.register_page(__name__, path='/')


def layout():
    """Show the welcome message"""
    fig, df = project_counts()
    return [
        html.H2("Welcome"),
        html.Hr(className="my-2"),
        html.P(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."),
        dcc.Graph(figure=fig)
    ]
