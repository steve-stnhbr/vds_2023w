import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, State

from map import *
from pop_structure import *

HEADING = "Differences between urban and rural areas in the EU"

df_population_density = sort_to_numeric_bfill(pd.read_csv("data/density.tsv", dtype={'geo': str}))

app = Dash(__name__)


app.layout = html.Div([
    html.H1(HEADING),
    html.Div([
        html.H2("Population Density by NUTS3 Region"),
        dcc.Graph(id="center_map", 
              figure=create_map_graph(None, df_population_density.geo, df_population_density["2022"], level=3)),
    ]),
    html.Div([
        html.H2("Age Distribution by NUTS3 Region"),
        dcc.Dropdown(id="age_group_select", options=[{"label": group, "value": group} for group in POP_AGE_GROUPS.keys()], value="fine"),
        dcc.Graph(id="population_graph", figure=create_population_structure_bar_chart(None))
    ])
])


@app.callback(
    Output("center_map", "figure"),
    [Input("center_map", "clickData")],
    [State("center_map", "figure")],
)
def update_map(figure, click_data):
    if click_data is None:
        return figure
    else:
        create_map_graph(figure, ["DE", "FR"], [1, 1])
        return figure
    
@app.callback(
    Output("population_graph", "figure"),
    [Input("center_map", "selectedData"), Input('age_group_select', 'value')],
    [State("population_graph", "figure")],
)
def update_population_graph(selected_data, age_group, figure):
    if selected_data is None:
        return create_population_structure_bar_chart(figure, groups=age_group)
    return create_population_structure_bar_chart(figure, geos=[datum['location'] for datum in selected_data['points']], groups=age_group)


if __name__ == '__main__':
    app.run_server(debug=True)

