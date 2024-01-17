import plotly.graph_objects as go
import pandas as pd

from lib.geo import *
from lib.graphics import *
from lib.geojson import get_zoom_center
from lib.style import *
from lib.util import *

GEO_IDENTIFIER = 'properties.NUTS_ID'
NUTS_LEVEL = 3

BASE_OPACITY = .58
HIGHLIGHT_OPACITY = .85
UNHIGHLIGHT_OPACITY = .3
SELECTED_OPACITY = .7
SELECTED_UNHIGHLIGHT_OPACITY = .5

HIGHLIGHT_VALUE = 1
UNHIGHLIGHT_VALUE = .1

HIGHLIGHT_MULTIPLIER = 1.5

NO_DENSITY_VALUE = 1000

DEFAULT_ZOOM = 2.1619232547722014
DEFAULT_CENTER = {'lon': 9.134555477446042, 'lat': 56.96554633630714}

LOG_COLORSCALE = logarithmic_color_scale(pc.sequential.Purples, base=3.1, num_samples=100)

LOG_COLORSCALES = {urban_type: logarithmic_color_scale(URBAN_TYPE_COLORSCALES_R[urban_type], base=3.1, num_samples=100) for urban_type in URBAN_TYPES.values()}

HOVERTEMPLATE = "<b>%{text} (%{location})</b><br>Population density: %{z:.2f}k people per km²<br>Urban type: <b>%{customdata}</b>"

df_population_density = pd.read_csv(ROOT_DIR + "data/density.tsv", dtype={'geo': str})
df_population_density = df_population_density[df_population_density.apply(lambda row: geo_is_level(row['geo'], 3), axis=1)]
df_population_density = sort_to_numeric_ffill(df_population_density)
df_population_density = assign_urbanization_type(df_population_density)
years_population_density = get_years(df_population_density)

def create_map_graph(fig, highlight_locations=[], level=3, year=2022, selected_data=[], color_urban_types=True, color_population_density=True):
    global df_population_density
    if str(year) not in years_population_density:
        raise NoDataAvailableError(year=year)
    locations = df_population_density['geo']
    values = df_population_density[str(year)]
    max_value = df_population_density[years_population_density].max().max()
    min_value = df_population_density[years_population_density].min().min()

    values = values
    if len(intersection(URBAN_TYPES.values(), highlight_locations)) > 0:
        highlight_locations = get_geos_with_urban_types(highlight_locations)
    # only highlight regions that are also selected
    if selected_data is not None and len(selected_data) > 0:
        highlight_locations = intersection(highlight_locations, selected_data)

    #locations = df_population_density[~df_population_density['geo'].isin(highlight_locations + selected_data)]['geo']
    if fig is None:
        # divide dataframe by urban type
        fig = create_figure()
        fig.update_layout(go.Layout(
                    mapbox_style="carto-positron",
                    mapbox_zoom=2.1619232547722014,
                    mapbox_center = {'lon': 9.134555477446042, 'lat': 56.96554633630714},
                    margin={"r":0,"t":0,"l":0,"b":0},
                    title=f"Population density in NUTS{level} regions",
            )
        )

        for urban_type in URBAN_TYPES.values():
            df_population_density_use = df_population_density[~df_population_density['geo'].isin(list(highlight_locations) + list(selected_data))]
            df_population_density_use = df_population_density[df_population_density['urban_type'] == urban_type]
            locations = df_population_density_use['geo']
            values = df_population_density_use[str(year)]
            fig.add_trace(
                go.Choroplethmapbox(
                    geojson=current_geojson,
                    locations=locations,
                    featureidkey=GEO_IDENTIFIER,
                    z=values if color_population_density else [NO_DENSITY_VALUE]*len(locations),
                    marker={'opacity': BASE_OPACITY, "line":  {"width": .1}},
                    colorscale=LOG_COLORSCALES[urban_type] if color_urban_types else LOG_COLORSCALE,
                    text=pd.DataFrame(locations).apply(lambda x: get_geo_name(x['geo']) or x['geo'], axis=1),
                    hovertemplate=HOVERTEMPLATE,
                    customdata=[urban_type]*len(locations),
                    showscale=False,
                    zmin=min_value,
                    zmax=max_value,
                )
            )
    else:
        update_existing_traces(fig, df_population_density, highlight_locations, selected_data, color_urban_types, color_population_density, year, min_value, max_value)
    if selected_data is not None and len(selected_data) > 0:
        zoom, center = get_zoom_center(selected_data)
        fig['layout']['mapbox']['zoom'] = zoom
        fig['layout']['mapbox']['center'] = center
    fig['layout']['coloraxis']['cmin'] = min_value
    fig['layout']['coloraxis']['cmax'] = max_value
    return fig

def update_existing_traces(fig, df_population_density, highlight_locations, selected_data, color_urban_types, color_population_density, year, min_value, max_value):
    fig['data'] = fig['data'][:len(URBAN_TYPES.values())]
    opacity = UNHIGHLIGHT_OPACITY if len(highlight_locations) > 0 or len(selected_data) > 0 else BASE_OPACITY
    for i, urban_type in enumerate(URBAN_TYPES.values()):
        data = fig['data'][i]
        chunk = df_population_density[~df_population_density['geo'].isin(list(highlight_locations) + list(selected_data))]
        chunk = df_population_density[df_population_density['urban_type'] == urban_type]
        values = chunk[str(year)]
        data['z'] = values if color_population_density else [NO_DENSITY_VALUE]*len(chunk)
        data['marker']['opacity'] = opacity
        data['colorscale'] = LOG_COLORSCALES[urban_type] if color_urban_types else LOG_COLORSCALE
        data['locations'] = chunk['geo']
        data['text'] = pd.DataFrame(chunk['geo']).apply(lambda x: get_geo_name(x['geo']) or x['geo'], axis=1)
    # add selected traces
    if len(selected_data) > 0:
        add_selected_traces(fig, df_population_density, selected_data, color_urban_types, color_population_density, year, highlight_locations, min_value, max_value)
    # add highlighted traces
    if len(highlight_locations) > 0:
        add_highlighted_traces(fig, df_population_density, highlight_locations, color_urban_types, color_population_density, year, min_value, max_value)
        

def add_selected_traces(fig, df_population_density, selected_data, color_urban_types, color_population_density, year, highlight_locations, min_value, max_value):
    df_selected = df_population_density[df_population_density['geo'].isin(selected_data)]
    for urban_type in get_urban_types_of_geos(selected_data, as_string=True, unique=True):
        locations, values = df_selected[df_selected['urban_type'] == urban_type][['geo', str(year)]].values.T
        fig['data'].append(
            go.Choroplethmapbox(
                geojson=current_geojson,
                locations=locations,
                featureidkey=GEO_IDENTIFIER,
                z=values if color_population_density else [NO_DENSITY_VALUE]*len(locations),
                marker={'opacity': SELECTED_OPACITY if len(highlight_locations) == 0 else SELECTED_UNHIGHLIGHT_OPACITY, "line":  {"width": .3}},
                colorscale=LOG_COLORSCALES[urban_type] if color_urban_types else LOG_COLORSCALE,
                text=df_selected.apply(lambda x: get_geo_name(x['geo']) or x['geo'], axis=1),
                hovertemplate=HOVERTEMPLATE,
                customdata=[urban_type]*len(locations),
                showscale=False,
                zmin=min_value,
                zmax=max_value,
            )
        )

def add_highlighted_traces(fig, df_population_density, highlight_locations, color_urban_types, color_population_density, year, min_value, max_value):
    for urban_type in get_urban_types_of_geos(highlight_locations, as_string=True, unique=True):
        locations, values = df_population_density[df_population_density['geo'].isin(highlight_locations)][['geo', str(year)]].values.T
        fig['data'].append(
            go.Choroplethmapbox(
                geojson=current_geojson,
                locations=highlight_locations,
                featureidkey=GEO_IDENTIFIER,
                z=values if color_population_density else [NO_DENSITY_VALUE]*len(locations),
                marker={'opacity': HIGHLIGHT_OPACITY, "line":  {"width": 1}},
                colorscale=LOG_COLORSCALES[urban_type] if color_urban_types else LOG_COLORSCALE,
                text=pd.DataFrame(highlight_locations, columns=['geo']).apply(lambda x: get_geo_name(x['geo']) or x['geo'], axis=1),
                hovertemplate=HOVERTEMPLATE,
                customdata=[urban_type]*len(locations),
                showscale=False,
                zmin=min_value,
                zmax=max_value,
            )
        )