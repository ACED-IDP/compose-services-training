import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc
import logging

logger = logging.getLogger('dash')


def histogram_figures(histograms):
    """An array of histograms figures, dataframes and names.
    @return fig[], df[], name[]"""

    dfs = []
    figs = []
    names = []

    assert len(histograms._aggregation.keys()) == 1  # noqa
    entity = list(histograms._aggregation.keys())[0]  # noqa
    for k, v in histograms._aggregation[entity].items():  # noqa
        v.name = k
        df = pd.DataFrame(v.histogram)
        fig = px.histogram(df, x="key", y="count", title=v.name, log_y=len(v.histogram) > 1,
                           id={
                               'index': f"{entity}-{k}",
                               'type': 'query-parameter'
                           }
                           )
        fig.update_layout(legend=dict(orientation="h", title=None),
                          yaxis_title=None, xaxis_title=None,
                          plot_bgcolor='rgba(0,0,0,0)'
                          )

        figs.append(fig)
        dfs.append(df)
        names.append(v.name)

    return figs, dfs, names


def histogram_selects(histograms):
    """An array of histograms checklists dataframes, and names.
    @return fig[], df[], name[]"""

    dfs = []
    checklists = []
    names = []

    assert len(histograms._aggregation.keys()) == 1  # noqa
    entity = list(histograms._aggregation.keys())[0]  # noqa
    for k, v in histograms._aggregation[entity].items():  # noqa
        v.name = k
        if not any([isinstance(h.key, str) for h in v.histogram]):
            continue
        df = pd.DataFrame(v.histogram)
        checklist = dcc.Checklist(
            id={
                'index': f"{entity}-{k}",
                'type': 'query-parameter'
            },
            options=[
                {
                    'value': str(h.key),
                    'label': html.Div(
                         [
                             html.Div(h.key),
                             dbc.Badge(h.count, className="ms-1", color="info")
                         ],
                         style={'display': 'inline-flex', 'paddingLeft': '2em'}
                    )
                }
                for h in v.histogram
            ],
            labelStyle={'display': 'flex'}
        )

        checklists.append(checklist)
        dfs.append(df)
        names.append(v.name)

    return checklists, dfs, names


def histogram_sliders(histograms):
    """An array of histograms sliders dataframes, and names.
    @return slider[], df[], name[]"""

    dfs = []
    sliders = []
    names = []

    assert len(histograms._aggregation.keys()) == 1  # noqa
    entity = list(histograms._aggregation.keys())[0]  # noqa
    for k, v in histograms._aggregation[entity].items():  # noqa
        v.name = k
        if any([isinstance(h.key, str) for h in v.histogram]):
            continue
        if not any([isinstance(h.key, list) for h in v.histogram]):
            continue

        assert len(v.histogram) == 1
        df = pd.DataFrame(v.histogram)
        min_ = v.histogram[0].key[0]
        max_ = v.histogram[0].key[1]
        # value = max_,
        sliders.append(
            dcc.Slider(min_, max_, int((max_ - min_)/10),
                       id={
                           'index': f"{entity}-{k}",
                           'type': 'query-parameter'
                       }
                       )
        )

        dfs.append(df)
        names.append(v.name)

    return sliders, dfs, names
