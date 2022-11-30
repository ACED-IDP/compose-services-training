import logging

import dash_bootstrap_components as dbc
import pandas as pd
from util import get_authz, get_submission_service

import dash
from dash import Input, Output, callback, dash_table, html

logger = logging.getLogger('dash')


dash.register_page(__name__)


def layout():
    # query_service = get_submission_service()
    # data = query_service.query("{ program(first:0) { id name projects { id code } } }")
    # logger.error(data)

    simplified_authz = {k: ','.join([m['method'] for m in v]) for k, v in get_authz().items()}
    df = pd.DataFrame([{'path': k, 'methods': v} for k, v in simplified_authz.items()])
    if 'path' in df:
        df['id'] = df['path']
        df.set_index('id', inplace=True, drop=False)

    return [
        html.H2("Authorization"),
        html.P(
            "You have the following authorization profile.",
            className="lead",
        ),
        html.Hr(className="my-2"),
        dbc.Label('Select a row:'),
        # see https://stackoverflow.com/questions/61905396/dash-datatable-with-select-all-checkbox
        # more tricks https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/DataTable/Tips-and-tricks/filter-datatable.py
        dash_table.DataTable(df.to_dict('records'),
                             columns=[
                                 {'name': i, 'id': i, 'deletable': False} for i in df.columns
                                 # omit the id column
                                 if i != 'id'
                             ],
                             id='tbl',
                             row_selectable='multi',
                             page_current=0,
                             page_size=10,
                             sort_action='native',
                             cell_selectable=False,
                             ),
        dbc.Alert(id='tbl_out'),
    ]


@callback(Output('tbl_out', 'children'),
          Input('tbl', 'derived_virtual_row_ids'),
          Input('tbl', 'selected_row_ids')
          )
def update_graphs(row_ids, selected_row_ids):
    return str(selected_row_ids)

