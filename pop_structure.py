import plotly.graph_objects as go
import plotly.colors as pc
import pandas as pd

from lib.transformations import *
from lib.geo import *
from lib.style import *
from lib.util import *
import time

HEADING_REGION = "Age Distribution by NUTS3 Region"
HEADING_URBAN_TYPE = "Age Distribution by Urban Type"

HOVER_TEMPLATE = "<b>%{y}%</b>"

UNSELECTED_OPACITY = .43

MAX_GEOS_AT_ONCE = 3

POP_AGE_GROUPS_FINE = {
    "PC_Y0_14": "0-14",
    "PC_Y15_19": "15-19",
    "PC_Y20_24": "20-24",
    "PC_Y25_29": "25-29",
    "PC_Y30_34": "30-34",
    "PC_Y35_39": "35-39",
    "PC_Y40_44": "40-44",
    "PC_Y45_49": "45-49",
    "PC_Y50_54": "50-54",
    "PC_Y55_59": "55-59",
    "PC_Y60_64": "60-64",
    "PC_Y65_69": "65-69",
    "PC_Y70_74": "70-74",
    "PC_Y75_79": "75-79",
    "PC_Y80_MAX": "80+",
}

POP_AGE_GROUPS_COARSE = {
    "PC_Y0_14": "0-14",
    "PC_Y15_24": "15-24",
    "PC_Y25_49": "25-49",
    "PC_Y50_64": "50-64",
    "PC_Y65_79": "65-79",
    "PC_Y80_MAX": "80+",
}

POP_AGE_GROUPS_VCOARSE = {
    "PC_Y0_19": "0-19",
    "PC_Y20_39": "20-39",
    "PC_Y40_59": "40-59",
    "PC_Y60_79": "50-79",
    "PC_Y80_MAX": "80+",
}

POP_AGE_GROUPS = {
    "very_coarse": POP_AGE_GROUPS_VCOARSE,
    "coarse": POP_AGE_GROUPS_COARSE,
    "fine": POP_AGE_GROUPS_FINE,
}

COLOR_OFFSET = 5

state_before0 = []
state_before1 = []
trace_before0 = []
trace_before1 = []

# add colors to the age groups
for age_group in POP_AGE_GROUPS.values():
    for i, (ag_id, name) in enumerate(age_group.items()):
        #age_group[ag_id] = {"name": name, "color": pc.sample_colorscale(pc.sequential.Plotly3, i/len(age_group))}
        age_group[ag_id] = {"name": name, "color": {urban_type: pc.sample_colorscale(URBAN_TYPE_COLORSCALES[urban_type], i/(len(age_group) + COLOR_OFFSET)) for urban_type in URBAN_TYPES.values()}}

df_pop_structure = pd.read_csv(ROOT_DIR + "data/population_structure_indicators.tsv", dtype={'geo': str})
years_pop_structure = get_years(df_pop_structure)
df_pop_structure = df_pop_structure[(df_pop_structure['freq'] == "A") & (df_pop_structure['unit'] == "PC")]
df_pop_structure = df_pop_structure.drop(df_pop_structure.columns.difference(['geo', 'indic_de'] + years_pop_structure), axis=1)
df_pop_structure = df_pop_structure[df_pop_structure.apply(lambda row: geo_is_level(row['geo'], 3), axis=1)]
df_pop_structure = sort_to_numeric_ffill(df_pop_structure)
df_pop_structure = assign_urbanization_type(df_pop_structure)
years_pop_structure = get_years(df_pop_structure)
df_pop_structure_grouped = df_pop_structure.groupby(['urban_type', 'indic_de', 'geo']).mean().reset_index()

def create_population_structure_bar_chart_traces(fig, year='2022', geos=[], groups="fine", selected=[], id=0):
    global df_pop_structure
    if year is not None and year not in years_pop_structure:
        raise NoDataAvailableError(year=year)
    fig = create_figure()

    df_pop = df_pop_structure.loc[:, ['indic_de', 'geo', 'urban_type', year]]
    if geos is not None and len(geos) > 0:
        df_pop = df_pop[df_pop['geo'].isin(geos)]

    # only display MAX_GEOS_AT_ONCE NUTS3 regions at once, otherwise aggregate them by urban_types
    if len(df_pop['geo']) > MAX_GEOS_AT_ONCE:
        heading = HEADING_URBAN_TYPE
        age_group = POP_AGE_GROUPS[groups]
        selected = get_urban_types_of_geos(selected)

        for i, (ag_id, values) in enumerate(age_group.items()):
            chunk = df_pop[df_pop['indic_de'] == ag_id]
            for urban_type in URBAN_TYPES.values():
                opacity = 1 if urban_type in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1
                color = values['color'][urban_type]
                color = add_opacity_to_color(color, opacity)
                fig.add_trace(
                    go.Bar(
                        ids=[urban_type],
                        x=[urban_type],
                        y=chunk[chunk['urban_type'] == urban_type][year],
                        name=values['name'],
                        customdata=[id],
                        hovertemplate=HOVER_TEMPLATE,
                        showlegend=False,
                        marker_color=color
                    )
                )
            
    else: # otherwise display all NUTS3 regions
        for i, (ag_id, values) in enumerate(POP_AGE_GROUPS[groups].items()):
            heading = HEADING_REGION
            chunk = df_pop[df_pop['indic_de'] == ag_id]
            for geo in chunk['geo'].unique():
                row = chunk[chunk['geo'] == geo]
                opacity = 1 if geo in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1
                fig.add_trace(
                    go.Bar(
                        ids=[geo],
                        x=[geo],
                        y=row[year],
                        name=values['name'],
                        customdata=[id],
                        hovertemplate=HOVER_TEMPLATE,
                        showlegend=False,
                        marker_color=add_opacity_to_color(values['color'][row['urban_type'].values[0]], opacity=opacity)
                    )
                )

    fig.update_layout(barmode='stack')

    # add legend
    for urban_type in set(URBAN_TYPE_COLORSCALES.keys()) - {'unavailable'}:
        fig.add_trace(
            go.Bar(
                x=[None],
                y=[None],
                name=urban_type,
                marker_color=URBAN_TYPE_COLORS[urban_type],
            )
        )
    
    return fig


def create_population_structure_bar_chart(fig, year='2022', geos0=[], geos1=[], groups="fine", selected0=[], selected1=[]):
    global state_before0, state_before1, trace_before0, trace_before1
    state0 = [year, geos0, groups, selected0]
    state1 = [year, geos1, groups, selected1]
    fig = create_figure()
    if not list_equals(state_before0, state0):
        traces0 = create_population_structure_bar_chart_traces(fig, year, geos0, groups, selected0, 0)
        fig.add_traces(traces0.data, rows=1, cols=1)
        state_before0 = state0
        trace_before0 = traces0
        fig.update_layout(traces0.layout)
    else:
        fig.add_traces(trace_before0.data, rows=1, cols=1)
        fig.update_layout(trace_before0.layout)
    if not list_equals(state_before1, state1):
        traces1 = create_population_structure_bar_chart_traces(fig, year, geos1, groups, selected1, 1)
        fig.add_traces(traces1.data, rows=1, cols=2)
        state_before1 = state1
        trace_before1 = traces1
        fig.update_layout(traces1.layout)
    else :
        fig.add_traces(trace_before1.data, rows=1, cols=2)
        fig.update_layout(trace_before1.layout)
    return fig