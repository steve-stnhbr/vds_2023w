import numpy as np
import plotly.colors as pc

def logarithmic_color_scale(base_colorscale, base=1.5, num_samples=100, reverse=False):
    # Modify the colorscale to visually represent logarithmic scale without transforming the data
    log_scale = np.linspace(0, 1, num_samples) ** base
    color_samples = pc.sample_colorscale(base_colorscale, np.linspace(1 if reverse else 0, 0 if reverse else 1, num_samples))
    modified_colors = [[scale, color_sample] for scale, color_sample in zip(log_scale, color_samples)]
    return modified_colors