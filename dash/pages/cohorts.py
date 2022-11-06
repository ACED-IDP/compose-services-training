import logging

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, ALL, callback, MATCH, State
from figures.histogram import histogram_selects, histogram_sliders
from inflection import titleize, pluralize
from models.file import get_file_histograms
from models.observation import get_observation_histograms
# Define recursive dictionary
from collections import defaultdict
import json
import collections

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
    logger.error(('display_filters', values, ids))
    filters = build_filters(values, ids)
    return json.dumps(filters, indent=4)


@callback(
    Output({'type': 'term-count', 'index': MATCH}, 'children'),
    Input({'type': 'query-parameter', 'index': MATCH}, 'value'),
    State({'type': 'query-parameter', 'index': MATCH}, 'id')
)
def update_counters(values, ids):
    """Run a histogram and then update badges."""
    logger.error(('update_counters', values, ids))
    return ''
    # filters = build_filters(values, ids)
    # if 'file' in filters:
    #     file_histograms = get_file_histograms(variables=filters['file'])
    #     logger.error(file_histograms)
    # return json.dumps(filters, indent=4)


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

    return [
        html.H2("Cohorts"),
        html.Hr(className="my-2"),
        html.P('Quis imperdiet massa tincidunt nunc. Convallis tellus id interdum velit. Mauris pellentesque pulvinar pellentesque habitant morbi tristique senectus.'),
        html.Hr(className="my-2"),
        html.Code(
            id="query-builder",
            children="Selections go here..."),
        dbc.Tabs(
            [
                dbc.Tab(file_accordian, label="Files"),
                dbc.Tab(observation_accordian, label="Observations"),
            ]
        )
    ]

