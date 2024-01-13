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

LOG_COLORSCALE = logarithmic_color_scale(pc.sequential.Purples, base=3.1, num_samples=100)

HOVERTEMPLATE = "<b>%{text}</b><br>Population density: %{z:.2f} people per km²"

df_population_density = sort_to_numeric_ffill(pd.read_csv("data/density.tsv", dtype={'geo': str}))
df_population_density = df_population_density[df_population_density.apply(lambda row: geo_is_level(row['geo'], 3), axis=1)]
years_population_density = get_years(df_population_density)

def create_map_graph(fig, highlight_locations=[], level=3, year=2022, selected_data=[]):
    global df_population_density
    if str(year) not in years_population_density:
        raise NoDataAvailableError(year=year)
    locations = df_population_density['geo']
    values = df_population_density[str(year)]
    # if necessary convert urban_types to NUTS3-ID
    if len(intersection(URBAN_TYPES.values(), highlight_locations)) > 0:
        highlight_locations = get_geos_with_urban_types(highlight_locations)
    # only highlight regions that are also selected
    if selected_data is not None and len(selected_data) > 0:
        highlight_locations = intersection(highlight_locations, selected_data)
    if fig is None:
        fig = create_figure()
        fig.update_layout(go.Layout(
                    mapbox_style="carto-positron",
                    mapbox_zoom=2.1619232547722014,
                    mapbox_center = {'lon': 9.134555477446042, 'lat': 56.96554633630714},
                    margin={"r":0,"t":0,"l":0,"b":0},
                    title=f"Population density in NUTS{level} regions"
            )
        )
        fig.add_trace(
            go.Choroplethmapbox(
                geojson=get_nuts_geojson(level, year),
                locations=locations,
                featureidkey=GEO_IDENTIFIER,
                z=values,
                marker={'opacity': BASE_OPACITY, "line":  {"width": .1}},
                colorscale=LOG_COLORSCALE,
                text=pd.DataFrame(df_population_density['geo']).apply(lambda x: get_geo_name(x['geo']) or x['geo'], axis=1),
                hovertemplate=HOVERTEMPLATE,
                hoverinfo=None
            )
        )
    else:
        fig['data'][0]['z'] = values
        fig['data'][0]['colorscale'] = LOG_COLORSCALE
        fig['data'] = [fig['data'][0]]
        fig['data'][0]['marker']['opacity'] = UNHIGLIGHT_OPACITY if len(highlight_locations) > 0 else BASE_OPACITY
        fig['data'].append(go.Choroplethmapbox(
            geojson=get_nuts_geojson(NUTS_LEVEL, year),
            locations=highlight_locations,
            featureidkey=GEO_IDENTIFIER,
            z=[1]*len(highlight_locations),
            marker={'opacity': HIGHLIGHT_OPACITY, "line":  {"width": .1}},
            showlegend=False,
            showscale=False
        ))
    if selected_data is not None and len(selected_data) > 0:
        zoom, center = get_zoom_center(selected_data)
        fig['layout']['mapbox']['zoom'] = zoom
        fig['layout']['mapbox']['center'] = center
    return fig