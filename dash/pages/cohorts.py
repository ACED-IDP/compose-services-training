import collections
import json
import logging

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, ALL, callback, get_app, dash_table
from figures.histogram import histogram_selects, histogram_sliders
from inflection import titleize, pluralize
from models.file import get_file_histograms, get_files
from models.observation import get_observation_histograms, get_patients

logger = logging.getLogger('dash')

dash.register_page(__name__)


def tree_dict():
    """A recursive default dict."""
    return collections.defaultdict(tree_dict)


def build_filters(values, ids):
    """Create a filter from selected values and ids."""
    filters = tree_dict()
    for value, id_ in zip(values, ids):
        if not value:
            continue
        entity, parameter = id_["index"].split('-')
        if 'AND' not in filters[entity]['filter']:
            filters[entity]['filter']['AND'] = []
        filters[entity]['filter']['AND'].append({'IN': {parameter: value}})
    return filters


@callback(
    Output('query-builder', 'children'),
    Input({'type': 'query-parameter', 'index': ALL}, 'value'),
    Input({'type': 'query-parameter', 'index': ALL}, 'id')
)
def display_filters(values, ids):
    """Build graphql filter."""
    filters = build_filters(values, ids)
    return json.dumps(filters, indent=4)


@callback(
    Output('histogram-data', 'data'),
    Input({'type': 'query-parameter', 'index': ALL}, 'value'),
    Input({'type': 'query-parameter', 'index': ALL}, 'id')
)
def update_counters(values, ids):
    """Run a histogram and then update badges."""
    filters = build_filters(values, ids)
    histograms = {'_aggregation': {}}
    histogram_fetchers = {
        'file': get_file_histograms,
        'case': get_observation_histograms
    }
    for entity_name in histogram_fetchers.keys():
        fetcher = histogram_fetchers.get(entity_name)
        if fetcher:
            fetcher_results = fetcher(variables=filters.get(entity_name, {"filter": {"AND": []}}))
            for aggregation_name in fetcher_results['_aggregation']:
                histograms['_aggregation'][aggregation_name] = fetcher_results['_aggregation'][aggregation_name]
    return histograms


@callback(
    Output('results', 'data'),
    Input('query', 'n_clicks'),
    Input({'type': 'query-parameter', 'index': ALL}, 'value'),
    Input({'type': 'query-parameter', 'index': ALL}, 'id')
)
def query(n_clicks, values, ids):
    """Run a histogram and then update badges."""
    filters = build_filters(values, ids)
    patient_ids = get_patients(variables=filters.get('case', {"filter": {"AND": []}}))
    file_filters = filters.get('file', {"filter": {"AND": []}})
    file_filters['filter']['AND'].append({"IN": {"patient_id": patient_ids}})
    file_filters['sort'] = []
    files = get_files(variables=file_filters)
    return files


# Clientside callback: traverse histogram, match DOM with class name 'term-count' update counts in DOM directly
get_app().clientside_callback(
    """
    // traverse histogram, match DOM with class name 'term-count' update counts in DOM directly 
    async function(histograms) {
        // console.log('debug: histogram counters',histograms);
        if (Object.keys(histograms).length === 0) {
            // console.log("debug: empty histogram");
            return window.dash_clientside.no_update
        }
        // get all our badges into a lookup hash by id
        const termCounts = Array.from(document.getElementsByClassName('term-count'));
        const termCountLookup = {}
        termCounts.forEach((item) => termCountLookup[JSON.parse(item.id)['index']] = item)        
        // const entity_name = 'file' ;
        Object.keys(histograms._aggregation).forEach((entity_name) => {
            console.log('Updating badges', entity_name)
            const entity = histograms._aggregation[entity_name] ; 
            for (const property_name in entity) {
              const p = `${entity_name}-${property_name}`          
              entity[property_name].histogram.forEach((h) => {
                // TODO - check range sliders
                if (termCountLookup[`${p}-${h.key}`]) {
                    termCountLookup[`${p}-${h.key}`].innerText = h.count
                    // remove from array
                    delete termCountLookup[`${p}-${h.key}`]
                }
              }) ;
              // set items no longer in histogram to 0
              Object.keys(termCountLookup).forEach((k) => {
                if (k.startsWith(p)) {
                    termCountLookup[k].innerText = '0';
                }          
              }) ;                    
            }                 
        });
        // always return no update since we updated dom directly
        return window.dash_clientside.no_update
    }
    """,
    Output('placeholder-dummy', 'children'),
    Input('histogram-data', 'data'),
    prevent_initial_call=True
)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    # "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "25rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


def layout():
    """Render the cohort page."""

    def accordian(items_, dfs_, names_):
        """Create an accordian with items for each facet."""
        return html.Div(dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        item,
                    ],
                    title=f"{titleize(pluralize(name))}"
                )
                for item, df, name in zip(items_, dfs_, names_)
            ],
            start_collapsed=True,
            always_open=True
        ))

    # get the data from guppy and plot each aggregation
    file_histograms = get_file_histograms()

    items = []
    data_frames = []
    names = []

    for i, d, n in [histogram_selects(file_histograms), histogram_sliders(file_histograms)]:
        items.extend(i)
        data_frames.extend(d)
        names.extend(n)

    file_accordian = accordian(items, data_frames, names)

    observation_histograms = get_observation_histograms()

    items = []
    data_frames = []
    names = []

    for i, d, n in [histogram_selects(observation_histograms), histogram_sliders(observation_histograms)]:
        items.extend(i)
        data_frames.extend(d)
        names.extend(n)

    observation_accordian = accordian(items, data_frames, names)

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("Cohorts"),
                html.Hr(className="my-2"),
                html.P(
                    'Quis imperdiet massa tincidunt nunc. Convallis tellus id interdum velit. Mauris pellentesque pulvinar pellentesque habitant morbi tristique senectus.'),
                html.Hr(className="my-2"),
                html.Code(
                    id="query-builder",
                    children="Selections go here..."),
            ], style=CONTENT_STYLE),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab([html.P('Quis imperdiet massa tincidunt nunc...')], label="Conditions"),
                    dbc.Tab([html.P('Quis imperdiet massa tincidunt nunc...')], label="Medications"),
                    dbc.Tab([html.P('Quis imperdiet massa tincidunt nunc...')], label="Demographics"),
                    dbc.Tab(observation_accordian, label="Observations"),
                    dbc.Tab(file_accordian, label="Files"),
                ])
            ], style=SIDEBAR_STYLE),
            dbc.Col([
                html.Hr(className="my-2"),
                html.Button('Query', id='query', n_clicks=0, style={'display': 'flex', 'float': 'right'}),
                dash_table.DataTable(id='results'),
                dcc.Store(id='histogram-data', storage_type='local'),
                html.P(id='placeholder-dummy', hidden=True),
            ], style=CONTENT_STYLE)
        ])
    ])
