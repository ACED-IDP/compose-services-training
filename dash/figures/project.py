
import pandas as pd
import plotly.express as px
from inflection import titleize, pluralize
from models.project import project_detail_counts


def counts():
    """Horizontal bar graph.
    @return fig, df"""

    project_counts = list(project_detail_counts())
    flattened = []
    for p in project_counts:
        for k, v in p.items():
            f = {'name': p.project[0].name}
            if k == 'project':
                continue
            f['entity'] = titleize(pluralize(k.replace('_count', '')))
            f['count'] = v
            flattened.append(f)
    df = pd.DataFrame(flattened)
    fig = px.bar(df, x="count", y="entity", color='name', orientation='h',
                 hover_data=["name", "count"],
                 height=400,
                 log_x=True)
    fig.update_layout(legend=dict(orientation="h", title=None), yaxis_title=None, xaxis_title=None,
                      # paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)'
                      )
    return fig, df
