import plotly.graph_objects as go
import pandas as pd
from lib.geo import *
from lib.graphics import *

GEO_IDENTIFIER = 'properties.NUTS_ID'
NUTS_LEVEL = 3

def create_map_graph(fig, locations, values, highlight_locations=[], level=3, year=2022):
    if fig is None:
        fig = go.Figure(
            layout=go.Layout(
                    mapbox_style="carto-positron",
                    mapbox_zoom=3,
                    mapbox_center = {"lat": 50.0, "lon": 10.0},
                    margin={"r":0,"t":0,"l":0,"b":0},
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
            )
        )
    else:
        fig['data'][0]['z'] = values
        fig['data'][0]['colorscale'] = logarithmic_color_scale(pc.sequential.Reds, base=3.1, num_samples=100)
        fig['data'] = [fig['data'][0]]
        fig['data'][0]['marker']['opacity'] = .2 if len(highlight_locations) > 0 else .5
        fig['data'].append(go.Choroplethmapbox(
            geojson=get_nuts_geojson(NUTS_LEVEL, year),
            locations = highlight_locations,
            featureidkey=GEO_IDENTIFIER,
            z=[1]*len(highlight_locations),
            marker={'opacity': .7, "line":  {"width": .1}},
            showlegend=False,
            showscale=False
        ))
    return fig