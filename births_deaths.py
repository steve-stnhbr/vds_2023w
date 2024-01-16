import plotly.graph_objects as go
import pandas as pd
import plotly.colors as pc

from lib.transformations import *
from lib.geo import *
from lib.style import *
from lib.util import *

UNSELECTED_OPACITY = .12

MAX_GEOS_AT_ONCE = 20
HEADING_URBAN_TYPE = "Births and Deaths by Urban Type"
HEADING_REGION = "Births and Deaths by NUTS3 Region"

HOVER_TEMPLATE_DEATHS = "<b>%{y:.2s}</b> deaths in %{x}"
HOVER_TEMPLATE_BIRTHS = "<b>%{y:.2s}</b> births in %{x}"

COLOR_OFFSET = 2

DEATHS_COLORSCALE = pc.sequential.solar
BIRTHS_COLORSCALE = pc.sequential.Purples

LINE_WIDTH = 3

df_births = pd.read_csv(ROOT_DIR + "data/births.tsv", dtype={'geo': str})
df_births = df_births[df_births.apply(lambda row: geo_is_level(row['geo'], 3), axis=1)]
df_births = assign_urbanization_type(df_births)
df_births = sort_to_numeric_ffill(df_births)

df_deaths = pd.read_csv(ROOT_DIR + "data/deaths_total.tsv", dtype={'geo': str})
df_deaths = df_deaths[df_deaths.apply(lambda row: geo_is_level(row['geo'], 3), axis=1)]
df_deaths = assign_urbanization_type(df_deaths)
df_deaths = sort_to_numeric_ffill(df_deaths)

years_births = get_years(df_births)
years_deaths = get_years(df_deaths)
years = intersection(years_births, years_deaths)
years = sorted(years)


def create_births_deaths_line_plot(fig, geos=[], year=None, selected=[]):
    global df_births, df_deaths
    if year is not None and year not in years:
        raise NoDataAvailableError(year=year)

    if geos is None or len(geos) == 0:
        geos = df_births['geo'].unique()

    fig = create_figure()
    fig.update_yaxes(rangemode="tozero")
    fig.update_layout(hovermode="x unified")
    if len(geos) > MAX_GEOS_AT_ONCE:
        heading = HEADING_URBAN_TYPE
        if selected is not None and len(selected) > 0:
            selected = get_urban_types_of_geos(selected)
        df_births_use = df_births.groupby(['urban_type'])[years].sum().reset_index()
        length_births = len(set(df_births_use['urban_type'].unique().tolist()) - {'unavailable'})
        df_deaths_use = df_deaths.groupby(['urban_type'])[years].sum().reset_index()
        length_deaths = len(set(df_deaths_use['urban_type'].unique().tolist()) - {'unavailable'})
        total_births = df_births[years].sum().reset_index(drop=True)
        total_deaths = df_deaths[years].sum().reset_index(drop=True)

        fig.add_trace(
            go.Scatter(
                x=years,
                y=total_births,
                name="total (births)",
                opacity=1,
                line={
                    'color': 'grey',
                    'width': LINE_WIDTH
                },
                hovertemplate=HOVER_TEMPLATE_BIRTHS,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=years,
                y=total_deaths,
                name="total (deaths)",
                opacity=1,
                line={
                    'color': 'black',
                    'width': LINE_WIDTH
                },
                hovertemplate=HOVER_TEMPLATE_DEATHS,
            )
        )

        for urban_type in set(df_births_use['urban_type'].unique().tolist()) - {'unavailable'}:
            row_births = df_births_use[df_births_use['urban_type'] == urban_type]
            row_deaths = df_deaths_use[df_deaths_use['urban_type'] == urban_type]
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=row_births[years].values[0],
                    mode='lines',
                    name=f"{urban_type} (births)",
                    hovertemplate=HOVER_TEMPLATE_BIRTHS,
                    opacity=1 if urban_type in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1,
                    line={
                        'color': sample_color(BIRTHS_COLORSCALE, list(set(df_births['urban_type'].unique().tolist()) - {'unavailable'}).index(urban_type) + COLOR_OFFSET, length_births + COLOR_OFFSET),
                        'width': LINE_WIDTH
                    }
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=row_deaths[years].values[0],
                    mode='lines',
                    name=f"{urban_type} (deaths)",
                    hovertemplate=HOVER_TEMPLATE_DEATHS,
                    opacity=1 if urban_type in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1,
                    line={
                        'color': sample_color(DEATHS_COLORSCALE, list(set(df_deaths['urban_type'].unique().tolist()) - {'unavailable'}).index(urban_type) + COLOR_OFFSET, length_deaths + COLOR_OFFSET),
                        'width': LINE_WIDTH
                    }
                )
            )
    else:
        heading = HEADING_REGION
        total_births = df_births[df_births['geo'].isin(geos)][years].sum().reset_index()
        total_deaths = df_deaths[df_deaths['geo'].isin(geos)][years].sum().reset_index()
        fig.add_trace(
            go.Scatter(
                x=years,
                y=total_births,
                name="total",
                opacity=0,
                showlegend=False,
                hovertemplate=HOVER_TEMPLATE_BIRTHS
            )
        )
        fig.add_trace(
            go.Scatter(
                x=years,
                y=total_deaths,
                name="total",
                opacity=0,
                showlegend=False,
                hovertemplate=HOVER_TEMPLATE_DEATHS
            )
        )
        for geo in geos:
            row = df_births[df_births['geo'] == geo]
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=row[years].values[0],
                    mode='lines',
                    name=f"{get_geo_name(geo)} (births)",
                    hovertemplate=HOVER_TEMPLATE_BIRTHS,
                    opacity=1 if geo in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1,
                    line={
                        'color': sample_color(BIRTHS_COLORSCALE, geos.index(geo) + COLOR_OFFSET, len(geos) + COLOR_OFFSET),
                        'width': LINE_WIDTH
                    }
                )
            )
            row = df_deaths[df_deaths['geo'] == geo]
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=row[years].values[0],
                    mode='lines',
                    name=f"{get_geo_name(geo)} (deaths)",
                    hovertemplate=HOVER_TEMPLATE_DEATHS,
                    opacity=1 if geo in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1,
                    line={
                        'color': sample_color(DEATHS_COLORSCALE, geos.index(geo) + COLOR_OFFSET, len(geos) + COLOR_OFFSET),
                        'width': LINE_WIDTH
                    }
                )
            )
    if year is not None:
        x = years.index(year)
        fig.add_shape(xref='x', yref='paper', x0=x, x1=x, y0=0, y1=1, line=dict(color=colors['marker'], width=2, dash="dash"))
    return fig
    