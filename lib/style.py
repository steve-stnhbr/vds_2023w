import plotly.graph_objs as go
import plotly.colors as pc

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
    return go.Figure(layout=DEFAULT_FIGURE_LAYOUT)

def sample_color(colorscale, index, total):
    return colorscale[index * len(colorscale) // total]

def add_opacity_to_color(color, opacity):
    if type(color) is str and color.startswith('#'):
        color, _ = pc.convert_colors_to_same_type(color, colortype='tuple')
        color = color[0]
        color = f'rgba{color + (opacity,)}'
        return color
    if type(color) is str and color.startswith("rgb"):
        color = color.replace("rgb", "rgba")
        color = color.replace(")", f", {opacity})")
        return color
    if type(color) is tuple:
        return color + (opacity,)
    return color