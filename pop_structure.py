import plotly.graph_objects as go
import plotly.colors as pc
import pandas as pd

from lib.transformations import *
from lib.geo import *
from lib.style import *
from lib.util import *

HEADING_REGION = "Age Distribution by NUTS3 Region"
HEADING_URBAN_TYPE = "Age Distribution by Urban Type"

HOVER_TEMPLATE = "<b>%{y}%</b>"

UNSELECTED_OPACITY = .43

MAX_GEOS_AT_ONCE = 20
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

# add colors to the age groups
for age_group in POP_AGE_GROUPS.values():
    for i, (ag_id, name) in enumerate(age_group.items()):
        age_group[ag_id] = {"name": name, "color": pc.sample_colorscale(pc.sequential.Plotly3, i/len(age_group))}


df_pop_structure = pd.read_csv(ROOT_DIR + "data/population_structure_indicators.tsv", dtype={'geo': str})
df_pop_structure = df_pop_structure[(df_pop_structure['freq'] == "A") & (df_pop_structure['unit'] == "PC")]
df_pop_structure = df_pop_structure[df_pop_structure.apply(lambda row: geo_is_level(row['geo'], 3), axis=1)]
df_pop_structure = to_numeric(df_pop_structure)
years_pop_structure = get_years(df_pop_structure)

def create_population_structure_bar_chart(fig, year='2022', geos=[], groups="fine", selected=[]):
    global df_pop_structure
    if year is not None and year not in years_pop_structure:
        raise NoDataAvailableError(year=year)
    fig = create_figure()
    df_pop = df_pop_structure.loc[:, ['indic_de', 'geo', year]]
    if geos is not None and len(geos) > 0:
        df_pop = df_pop[df_pop['geo'].str.startswith(tuple(geos))]
    # only select NUTS3 regions TODO: maybe not do this
    df_pop = df_pop[df_pop['geo'].str.len() == 5]
    # only display MAX_GEOS_AT_ONCE NUTS3 regions at once, otherwise aggregate them by urban_types
    if len(df_pop['geo'].unique()) > MAX_GEOS_AT_ONCE:
        heading = HEADING_URBAN_TYPE
        df_pop = assign_urbanization_type(df_pop)
        df_pop = df_pop.groupby(['urban_type', 'indic_de'])[year].mean().reset_index()
        age_group = POP_AGE_GROUPS[groups]
        selected = get_urban_types_of_geos(selected)

        for i, (ag_id, values) in enumerate(age_group.items()):
            chunk = df_pop[df_pop['indic_de'] == ag_id]
            fig.add_trace(
                go.Bar(
                    ids=chunk['urban_type'],
                    x=chunk['urban_type'],
                    y=chunk[year],
                    name=values['name'],
                    customdata=[values['name']],
                    marker_color=chunk.urban_type.apply(lambda x: values['color'][0] if x in selected else add_opacity_to_color(values['color'][0], UNSELECTED_OPACITY) if selected is not None and len(selected) > 0 else values['color'][0]),
                    hovertemplate=HOVER_TEMPLATE,
                )
            )
    else: # otherwise display all NUTS3 regions
        for i, (ag_id, values) in enumerate(POP_AGE_GROUPS[groups].items()):
            heading = HEADING_REGION
            row = df_pop[df_pop['indic_de'] == ag_id]
            fig.add_trace(
                go.Bar(
                    ids=row['geo'],
                    x=row['geo'].apply(get_geo_name),
                    y=row[year],
                    name=values['name'],
                    customdata=[values['name']],
                    marker_color=values['color']*len(row['geo'].unique()),
                    hovertemplate=HOVER_TEMPLATE,
                    #opacity=row['urban_type'].apply(lambda x: 1 if x in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1).values
                )
            )

    fig.update_layout(barmode='stack')

    return fig



