import plotly.graph_objects as go
import pandas as pd
from lib.transformations import *
from lib.geo import *

HEADING_REGION = "Population Development by NUTS3 Region"
HEADING_URBAN_TYPE = "Population Development by Urban Type"

MAX_GEOS_AT_ONCE = 50

df_population = pd.read_csv("data/population.tsv", dtype={'geo': str})
df_population = to_numeric_bfill(df_population)

def create_population_line_plot(fig, geos=[], year=None):
    global df_population
    years = get_years(df_population)
    df_pop = df_population
    fig = go.Figure()
    if geos is None or len(geos) == 0:
        geos = df_pop['geo'].unique()

    # only select NUTS3 regions TODO: maybe not do this
    geos = [geo for geo in geos if len(geo) == 5]

    if len(geos) > MAX_GEOS_AT_ONCE:
        heading = HEADING_URBAN_TYPE
        df_pop = assign_urbanization_type(df_pop)
        df_pop = df_pop.groupby(['urban_type'])[years].sum().reset_index()
        for urban_type in df_pop['urban_type'].unique():
            row = df_pop[df_pop['urban_type'] == urban_type]
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=row[years].values[0],
                    mode='lines',
                    name=urban_type
                )
            )
    else:
        heading = HEADING_REGION
        for geo in geos:
            row = df_pop[df_pop['geo'] == geo]
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=row[years].values[0],
                    mode='lines',
                    name=get_geo_name(geo)
                )
            )
    if year is not None:
        x = years.index(year)
        fig.add_shape(xref='x', yref='paper', x0=x, x1=x, y0=0, y1=1, line=dict(color="RoyalBlue", width=3, dash="dashdot"))
    return fig