import plotly.graph_objects as go
import pandas as pd
import functools

from lib.transformations import *
from lib.geo import *
from lib.style import *
from lib.util import *

HEADING_REGION = "Population Development by NUTS3 Region"
HEADING_URBAN_TYPE = "Population Development by Urban Type"

UNSELECTED_OPACITY = .24
FILL_OPACITY = .4

MAX_GEOS_AT_ONCE = 3

HOVER_TEMPLATE = "<b>%{y:.2s}</b> inhabitants in %{x}"

df_population = pd.read_csv(ROOT_DIR + "data/population_january1st.tsv", dtype={'geo': str})
df_population = df_population[(df_population['age'] == "TOTAL") & (df_population['sex'] == "T")].reset_index()
df_population = df_population[df_population.apply(lambda row: geo_is_level(row['geo'], 3), axis=1)]
df_population = assign_urbanization_type(df_population)
df_population = sort_to_numeric_ffill(df_population)
years_population = get_years(df_population)

state_before0 = []
state_before1 = []
trace_before0 = []
trace_before1 = []

def create_population_line_plot_traces(fig, geos=[], year=None, selected=[], id=0):
    global df_population

    if year is not None and year not in years_population:
        raise NoDataAvailableError(year=year)

    df_pop = df_population
    fig = create_figure()
    fig.update_layout(hovermode="x unified")
    if geos is None or len(geos) == 0:
        geos = df_pop['geo'].unique()

    if len(geos) > MAX_GEOS_AT_ONCE:
        heading = HEADING_URBAN_TYPE
        if selected is not None and len(selected) > 0:
            if len(intersection(URBAN_TYPES.values(), selected)) == 0:
                selected = get_urban_types_of_geos(selected)
        df_pop = df_pop[df_pop['geo'].isin(geos)]
        df_pop = df_pop.groupby(['urban_type'])[years_population].sum().reset_index()
        # calculate the sum of all urban types for each year
        total_values = df_pop[years_population].sum().reset_index(drop=True)

        for urban_type in set(df_pop['urban_type'].unique().tolist()) - {'unavailable'}:
            row = df_pop[df_pop['urban_type'] == urban_type]
            opacity = 1 if urban_type in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1
            color = URBAN_TYPE_COLORS[urban_type]
            color_transparent = add_opacity_to_color(color, opacity)
            fig.add_trace(
                go.Scatter(
                    x=years_population,
                    y=row[years_population].values[0],
                    mode='lines',
                    name=urban_type,
                    opacity=opacity,
                    stackgroup='stack',
                    line={
                        'color': color_transparent,
                    },
                    fill='tonexty',
                    fillcolor=add_opacity_to_color(color, FILL_OPACITY),
                    hovertemplate=HOVER_TEMPLATE,
                    customdata=[id]
                )
            )
        fig.add_trace(
            go.Scatter(
                x=years_population,
                y=total_values,
                name="total",
                opacity=0,
                stackgroup='other',
                line={
                    'color': 'rgba(0,0,0,0)',
                    'width': 0
                },
                fill='none',
                fillcolor='rgba(0,0,0,0)',
                hovertemplate=HOVER_TEMPLATE,
                showlegend=False,
                customdata=[id]
            )
        )
    else:
        heading = HEADING_REGION
        total_values = df_pop[df_pop['geo'].isin(geos)][years_population].sum().reset_index(drop=True)
        for geo in geos:
            row = df_pop[df_pop['geo'] == geo]
            opacity = 1 if geo in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1
            color = URBAN_TYPE_COLORS[get_urban_types_of_geos([geo], as_string=True, unique=False).unique()[0]]

            color_transparent = add_opacity_to_color(color, opacity)
            fig.add_trace(
                go.Scatter(
                    x=years_population,
                    y=row[years_population].values[0],
                    mode='lines',
                    name=get_geo_name(geo),
                    opacity=opacity,
                    stackgroup='stack',
                    line={
                        'color': color_transparent,
                    },
                    fill='tonexty',
                    fillcolor=add_opacity_to_color(color, FILL_OPACITY),
                    hovertemplate=HOVER_TEMPLATE,
                    customdata=[id]
                )
            )
        fig.add_trace(
            go.Scatter(
                x=years_population,
                y=total_values,
                name="total",
                opacity=0,
                stackgroup='other',
                line={
                    'color': 'rgba(0,0,0,0)',
                    'width': 0
                },
                fill='none',
                fillcolor='rgba(0,0,0,0)',
                hovertemplate=HOVER_TEMPLATE,
                showlegend=False,
                customdata=[id]
            )
        )
    fig.update_traces(hovertemplate=HOVER_TEMPLATE)
    if year is not None:
        x = years_population.index(year)
        fig.add_shape(xref='x', yref='paper', x0=x, x1=x, y0=0, y1=1, line=dict(color=colors['marker'], width=2, dash="dash"))
    return fig

def create_population_line_plot(fig, geos0=[], geos1=[], year=None, selected0=[], selected1=[]):
    global state_before0, state_before1, trace_before0, trace_before1
    state0 = [year, geos0, selected0]
    state1 = [year, geos1, selected1]
    fig = create_figure()
    if not list_equals(state_before0, state0):
        traces0 = create_population_line_plot_traces(fig, geos0, year, selected0, 0)
        fig.add_traces(traces0.data, rows=1, cols=1)
        state_before0 = state0
        trace_before0 = traces0
        fig.update_layout(traces0.layout)
    else:
        fig.add_traces(trace_before0.data, rows=1, cols=1)
        fig.update_layout(trace_before0.layout)
    if not list_equals(state_before1, state1):
        traces1 = create_population_line_plot_traces(fig, geos1, year, selected1, 1)
        fig.add_traces(traces1.data, rows=1, cols=2)
        state_before1 = state1
        trace_before1 = traces1
        fig.update_layout(traces1.layout)
    else :
        fig.add_traces(trace_before1.data, rows=1, cols=2)
        fig.update_layout(trace_before1.layout)
    return fig
