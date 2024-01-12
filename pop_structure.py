import plotly.graph_objects as go
import pandas as pd
from lib.transformations import *
from lib.geo import *

MAX_GEOS_AT_ONCE = 20
POP_AGE_GROUPS_FINE = [
    "PC_Y0_14",
    "PC_Y15_19",
    "PC_Y20_24",
    "PC_Y25_29",
    "PC_Y30_34",
    "PC_Y35_39",
    "PC_Y40_44",
    "PC_Y45_49",
    "PC_Y50_54",
    "PC_Y55_59",
    "PC_Y60_64",
    "PC_Y65_69",
    "PC_Y70_74",
    "PC_Y75_79",
    "PC_Y80_MAX",
]

POP_AGE_GROUPS_COARSE = [
    "PC_Y0_14",
    "PC_Y15_24",
    "PC_Y25_49",
    "PC_Y50_64",
    "PC_Y65_79",
    "PC_Y80_MAX",
]

POP_AGE_GROUPS_VCOARSE = [
    "PC_Y0_19",
    "PC_Y20_39",
    "PC_Y40_59",
    "PC_Y60_79",
    "PC_Y80_MAX",
]

POP_AGE_GROUPS = {
    "fine": POP_AGE_GROUPS_FINE,
    "coarse": POP_AGE_GROUPS_COARSE,
    "vcoarse": POP_AGE_GROUPS_VCOARSE,
}


df_pop_structure = pd.read_csv("data/population_structure_indicators.tsv", dtype={'geo': str})
df_pop_structure = to_numeric_bfill(df_pop_structure)

def create_population_graph(fig, geos=[]):
    global df_pop_structure
    years = get_years(df_pop_structure)
    if geos is not None and len(geos) > 0:
        df_pop_structure = df_pop_structure[df_pop_structure['geo'].str.startswith(tuple(geos))]
    df_pop_structure = df_pop_structure[["indic_de", 'geo'] + years]
    print(df_pop_structure['indic_de'].unique())
    if fig is None:
        fig = go.Figure()
        for geo in df_pop_structure['geo'].unique():
            row = df_pop_structure[df_pop_structure['geo'] == geo]
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=row[row['indic_de'] == "MEDAGEPOP"],
                    mode='lines'
                )
            )
    else:
        fig['data'][0]['y'] = df_pop_structure["MEDAGEPOP"]
    return fig

def create_population_structure_bar_chart(fig, year='2022', geos=[], groups="fine"):
    global df_pop_structure
    fig = go.Figure()
    df_pop = df_pop_structure.loc[:, ['indic_de', 'geo', year]]
    if geos is not None and len(geos) > 0:
        df_pop = df_pop[df_pop['geo'].str.startswith(tuple(geos))]
    df_pop = df_pop[df_pop['geo'].str.len() == 5]
    #df_pop = df_pop[["indic_de", 'geo'] + years]
    # only display MAX_GEOS_AT_ONCE NUTS3 regions at once, otherwise aggregate them by urban_types
    if len(df_pop['geo'].unique()) > MAX_GEOS_AT_ONCE:
        df_pop = assign_urbanization_type(df_pop)
        df_pop = df_pop.groupby(['urban_type', 'indic_de'])[year].mean().reset_index()
        age_groups = POP_AGE_GROUPS[groups]
        for age_group in age_groups:
            row = df_pop[df_pop['indic_de'] == age_group]
            fig.add_trace(
                go.Bar(
                    x=row['urban_type'],
                    y=row[year],
                    name=age_group
                )
            )
    else: # otherwise display all NUTS3 regions
        for age_group in POP_AGE_GROUPS[groups]:
            row = df_pop[df_pop['indic_de'] == age_group]
            fig.add_trace(
                go.Bar(
                    x=row['geo'],
                    y=row[year],
                    name=age_group
                )
            )

    fig.update_layout(barmode='stack')

    return fig



