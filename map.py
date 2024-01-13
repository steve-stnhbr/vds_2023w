import plotly.graph_objects as go
import pandas as pd
from lib.geo import *
from lib.graphics import *

GEO_IDENTIFIER = 'properties.NUTS_ID'
NUTS_LEVEL = 3

HOVERTEMPLATE = "<b>%{text}</b><br>Population density: %{z:.2f} people per km²"

df_population_density = sort_to_numeric_ffill(pd.read_csv("data/density.tsv", dtype={'geo': str}))
years_population_density = get_years(df_population_density)

def create_map_graph(fig, highlight_locations=[], level=3, year=2022):
    global df_population_density
    locations = df_population_density['geo']
    values = df_population_density[str(year)]
    if len(intersection(URBAN_TYPES.values(), highlight_locations)) > 0:
        highlight_locations = get_geos_with_urban_types(highlight_locations)
    if fig is None:
        fig = go.Figure(
            layout=go.Layout(
                    mapbox_style="carto-positron",
                    mapbox_zoom=3.04751102102008,
                    mapbox_center = {"lat": 56.56730983530582, "lon": 8.87268008141507},
                    margin={"r":0,"t":0,"l":0,"b":0},
                    min_zoom=3.2,
                    height=800,
                    width=1200,
                    title=f"Population density in NUTS{level} regions"
            )
        )
        fig.add_trace(
            go.Choroplethmapbox(
                geojson=get_nuts_geojson(level, year),
                locations=locations,
                featureidkey=GEO_IDENTIFIER,
                z=values,
                marker={'opacity': .5, "line":  {"width": .1}},
                colorscale=logarithmic_color_scale(pc.sequential.Reds, base=3.1, num_samples=100),
                text=pd.DataFrame(df_population_density['geo']).apply(lambda x: get_geo_name(x['geo']) or x['geo'], axis=1),
                hovertemplate=HOVERTEMPLATE,
                hoverinfo=None
            )
        )
    else:
        fig['data'][0]['z'] = values
        fig['data'][0]['colorscale'] = logarithmic_color_scale(pc.sequential.Purples, base=3.1, num_samples=100)
        fig['data'] = [fig['data'][0]]
        fig['data'][0]['marker']['opacity'] = .2 if len(highlight_locations) > 0 else .5
        fig['data'].append(go.Choroplethmapbox(
            geojson=get_nuts_geojson(NUTS_LEVEL, year),
            locations=highlight_locations,
            featureidkey=GEO_IDENTIFIER,
            z=[1]*len(highlight_locations),
            marker={'opacity': .7, "line":  {"width": .1}},
            showlegend=False,
            showscale=False
        ))
    return fig