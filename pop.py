import plotly.graph_objects as go
import pandas as pd
from lib.transformations import *
from lib.geo import *
from lib.style import *

HEADING_REGION = "Population Development by NUTS3 Region"
HEADING_URBAN_TYPE = "Population Development by Urban Type"
UNSELECTED_OPACITY = .24

MAX_GEOS_AT_ONCE = 50

df_population = pd.read_csv("data/population.tsv", dtype={'geo': str})
df_density = pd.read_csv("data/density.tsv", dtype={'geo': str})
df_density = sort_to_numeric_ffill(df_density)
df_area = pd.read_csv("data/area.tsv", dtype={'geo': str})
df_area = sort_to_numeric_ffill(df_area)

# create population data by multiplying density and area for each year
df_density = df_density.set_index('geo')
df_area = df_area.set_index('geo')
for year in get_years(df_area):
    df_population.loc[:, year] = (df_density.loc[:, year] * df_area.loc[:, year] / 100).reset_index()[year]
df_population = sort_to_numeric_ffill(df_population)

def create_population_line_plot(fig, geos=[], year=None, selected=[]):
    global df_population
    years = get_years(df_population)
    df_pop = df_population
    fig = create_figure()
    if geos is None or len(geos) == 0:
        geos = df_pop['geo'].unique()

    # only select NUTS3 regions TODO: maybe not do this
    geos = [geo for geo in geos if len(geo) == 5]

    if len(geos) > MAX_GEOS_AT_ONCE:
        heading = HEADING_URBAN_TYPE
        if selected is not None and len(selected) > 0:
            selected = get_urban_types_of_geos(selected)
        df_pop = assign_urbanization_type(df_pop)
        df_pop = df_pop.groupby(['urban_type'])[years].sum().reset_index()
        for urban_type in set(df_pop['urban_type'].unique().tolist()) - {'unavailable'}:
            row = df_pop[df_pop['urban_type'] == urban_type]
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=row[years].values[0],
                    mode='lines',
                    name=urban_type,
                    opacity=1 if urban_type in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1
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
                    name=get_geo_name(geo),
                    opacity=1 if geo in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1
                )
            )
    if year is not None:
        x = years.index(year)
        fig.add_shape(xref='x', yref='paper', x0=x, x1=x, y0=0, y1=1, line=dict(color="RoyalBlue", width=3, dash="dashdot"))
    return fig