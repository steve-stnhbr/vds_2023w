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
UNHIGLIGHT_OPACITY = .4

HIGHLIGHT_VALUE = 1
UNHIGHLIGHT_VALUE = .1

HIGHLIGHT_MULTIPLIER = 1.5

NO_DENSITY_VALUE = .3

LOG_COLORSCALE = logarithmic_color_scale(pc.sequential.Purples, base=3.1, num_samples=100)

LOG_COLORSCALES = {urban_type: logarithmic_color_scale(URBAN_TYPE_COLORSCALES_R[urban_type], base=3.1, num_samples=100) for urban_type in URBAN_TYPES.values()}

HOVERTEMPLATE = "<b>%{text}</b><br>Population density: %{z:.2f} people per km²<br>Urban type: <b>%{customdata}</b>"

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
    # only highlight regions that are also selected
    if selected_data is not None and len(selected_data) > 0:
        highlight_locations = intersection(highlight_locations, selected_data)
    if fig is None:
        # divide dataframe by urban type
        fig = create_figure()
        fig.update_layout(go.Layout(
                    mapbox_style="carto-positron",
                    mapbox_zoom=2.1619232547722014,
                    mapbox_center = {'lon': 9.134555477446042, 'lat': 56.96554633630714},
                    margin={"r":0,"t":0,"l":0,"b":0},
                    title=f"Population density in NUTS{level} regions"
            )
        )

        for urban_type in URBAN_TYPES.values():
            df_population_density_use = df_population_density[df_population_density['urban_type'] == urban_type]
            locations = df_population_density_use['geo']
            values = df_population_density_use[str(year)]

            if len(intersection(URBAN_TYPES.values(), highlight_locations)) > 0:
                # urban_types are in selection
                if color_population_density:
                    # TODO: color the urban_types that are highlighted accordingly
                    values = df_population_density.apply(lambda row: row[str(year)] * HIGHLIGHT_MULTIPLIER if row['urban_type'] in highlight_locations else UNHIGHLIGHT_VALUE, axis=1)
                else:
                    values = [HIGHLIGHT_VALUE if urban_type in highlight_locations else UNHIGHLIGHT_VALUE] * len(locations)
            else:
                # geos are in selection
                if color_population_density:
                    # TODO: color the recions that are highlighted accordingly
                    values = values
                else:
                    values = df_population_density.apply(lambda row: HIGHLIGHT_VALUE if row['geo'] in highlight_locations else UNHIGHLIGHT_VALUE, axis=1)

            fig.add_trace(
                go.Choroplethmapbox(
                    geojson=current_geojson,
                    locations=locations,
                    featureidkey=GEO_IDENTIFIER,
                    z=values if color_population_density else [NO_DENSITY_VALUE]*len(locations),
                    marker={'opacity': BASE_OPACITY, "line":  {"width": .1}},
                    colorscale=LOG_COLORSCALES[urban_type] if color_urban_types else LOG_COLORSCALE,
                    text=pd.DataFrame(df_population_density_use['geo']).apply(lambda x: get_geo_name(x['geo']) or x['geo'], axis=1),
                    hovertemplate=HOVERTEMPLATE,
                    customdata=[urban_type]*len(locations),
                )
            )
    else:
        fig['data'] = fig['data'][:len(URBAN_TYPES.values())]
        for i, urban_type in enumerate(URBAN_TYPES.values()):
            data = fig['data'][i]
            chunk = df_population_density[df_population_density['urban_type'] == urban_type]
            values = chunk[str(year)]
            data['z'] = values if color_population_density else [NO_DENSITY_VALUE]*len(chunk)
            data['marker']['opacity'] = BASE_OPACITY if len(highlight_locations) == 0 else UNHIGLIGHT_OPACITY
            data['colorscale'] = LOG_COLORSCALES[urban_type] if color_urban_types else LOG_COLORSCALE
        if len(highlight_locations) > 0:
            if len(intersection(URBAN_TYPES.values(), highlight_locations)) > 0:
                highlight_locations = get_geos_with_urban_types(highlight_locations)
            highlight_locations = intersection(selected_data, highlight_locations) if selected_data is not None and len(selected_data) > 0 else highlight_locations
            urban_type = get_urban_types_of_geos(highlight_locations, as_string=True, unique=False).unique()[0]
            fig['data'].append(
                go.Choroplethmapbox(
                    geojson=current_geojson,
                    locations=highlight_locations,
                    featureidkey=GEO_IDENTIFIER,
                    z=values if color_population_density else [1]*len(locations),
                    marker={'opacity': HIGHLIGHT_OPACITY, "line":  {"width": .3}},
                    colorscale=LOG_COLORSCALES[urban_type] if color_urban_types else LOG_COLORSCALE,
                    text=pd.DataFrame(df_population_density['geo']).apply(lambda x: get_geo_name(x['geo']) or x['geo'], axis=1),
                    hovertemplate=HOVERTEMPLATE,
                    customdata=[urban_type]*len(locations),
                )
            )
    if selected_data is not None and len(selected_data) > 0:
        zoom, center = get_zoom_center(selected_data)
        fig['layout']['mapbox']['zoom'] = zoom
        fig['layout']['mapbox']['center'] = center
    return fig