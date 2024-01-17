import plotly.graph_objs as go
import plotly.colors as pc
from plotly.subplots import make_subplots

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'paper_background': '#ffffff',
    'graph_background': '#EAEAF2',
    'marker': 'rgba(99, 100, 190, 123)'
}

DEFAULT_FIGURE_LAYOUT = go.Layout(
    paper_bgcolor=colors['paper_background'],
    plot_bgcolor=colors['graph_background'],
    margin={"r":10,"t":50,"l":10,"b":50},
)

URBAN_TYPE_COLORSCALES = {
    "urban": pc.sequential.Purples_r,
    "rural": pc.sequential.Greens_r,
    "intermediate": pc.sequential.Oranges_r,
    "unavailable": pc.sequential.Greys_r,
}

URBAN_TYPE_COLORSCALES_R = {
    "urban": pc.sequential.Purples,
    "rural": pc.sequential.Greens,
    "intermediate": pc.sequential.Oranges,
    "unavailable": pc.sequential.Greys,
}

URBAN_TYPE_COLORS = {
    "urban": "#582F93",
    "rural": "#238B44",
    "intermediate": "#E25609",
    "unavailable": "#bdbdbd",
}

mapbox_style = {
    'version': 8,
    'name': 'Custom Style',
    'sprite': 'mapbox://sprites/mapbox/bright-v9',
    'glyphs': 'mapbox://fonts/mapbox/{fontstack}/{range}.pbf',
    'sources': {
        'mapbox-streets': {
            'type': 'vector',
            'url': 'mapbox://mapbox.mapbox-streets-v8',
        },
    },
    'layers': [
        {
            'id': 'background',
            'type': 'background',
            'paint': {'background-color': 'black'},  # Background color
        },
        {
            'id': 'land',
            'type': 'fill',
            'source': 'mapbox-streets',
            'source-layer': 'land',
            'paint': {'fill-color': 'green'},  # Land color
        },
        {
            'id': 'water',
            'type': 'fill',
            'source': 'mapbox-streets',
            'source-layer': 'water',
            'paint': {'fill-color': 'blue'},  # Water color
        },
        # Add more layers for roads, buildings, etc. as needed
    ],
}

def create_figure(temlpate="plotly_dark"):
    return make_subplots(rows=1, cols=2)

def sample_color(colorscale, index, total):
    return colorscale[index * len(colorscale) // total]

def add_opacity_to_color(color, opacity):
    if type(color) is list and len(color) == 1:
        color = color[0]
    if type(color) is str and color.startswith('#'):
        color, _ = pc.convert_colors_to_same_type(color, colortype='tuple')
        color = color[0]
        color = f'rgba{color + (opacity,)}'
    elif type(color) is str and color.startswith("rgb"):
        color = color.replace("rgb", "rgba")
        color = color.replace(")", f", {opacity})")
    elif type(color) is str and color.startswith("rgba"):
        color = color.replace(r", .*?\)", f", {opacity})")
    elif type(color) is tuple:
        return color + (opacity,)
    return color