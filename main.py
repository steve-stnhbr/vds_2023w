import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, State

from map import *
from pop_structure import *
from pop import *

HEADING = "Differences between urban and rural areas in the EU"


app = Dash(__name__)


app.layout = html.Div([
    html.H1(HEADING),
    html.Div([
        html.H2("Year"),
        
    dcc.Slider(step=None, marks={year: str(year) for year in years_population_density}, id='year_slider', value=int(years_population_density[-1])),
    ]),
    html.Div([
        html.H2("Population Density by NUTS3 Region", id="map_heading"),
        dcc.Graph(id="center_map", 
              figure=create_map_graph(None, level=3), clear_on_unhover=True),
        # debug button
        html.Button('Debug', id='debug_button', n_clicks=0),
    ]),
    html.Div([
        html.H2("Age Distribution by Region", id="pop_distr_heading"),
        dcc.Dropdown(id="age_group_select", options=[{"label": group, "value": group} for group in POP_AGE_GROUPS.keys()], value="fine"),
        dcc.Graph(id="pop_distr_graph", figure=create_population_structure_bar_chart(None), clear_on_unhover=True)
    ]),
    html.Div([
        html.H2("Population by Region", id="pop_heading"),
        dcc.Graph(id="pop_graph", figure=create_population_line_plot(None), clear_on_unhover=True)
    ]),
])


@app.callback(
    Output("center_map", "figure"),
    [
        Input('year_slider', 'value'), 
        Input('pop_distr_graph', 'hoverData'), 
        Input('pop_graph', 'hoverData'), 
        Input("pop_graph", "figure"), 
        Input("debug_button", "n_clicks")
    ],
    [State("center_map", "figure")],
)
def update_map(year, pop_distr_hover, pop_hover, pop_figure, _, figure):
    print(figure['layout'])
    highlighted = [pop_figure['data'][point['curveNumber']]['name'] for point in pop_hover['points']] if pop_hover is not None else []
    highlighted = highlighted + ([datum['x'] for datum in (pop_distr_hover['points'])] if pop_distr_hover is not None else [])
    return create_map_graph(figure, highlight_locations=highlighted, level=3, year=year)
    
@app.callback(
    Output("pop_distr_graph", "figure"),
    [Input("center_map", "selectedData"), Input('age_group_select', 'value'), Input('year_slider', 'value')],
    [State("pop_distr_graph", "figure")]
)
def update_pop_distr_grap(selected_data, age_group, year, figure):
    year = str(year)
    if selected_data is None:
        fig = create_population_structure_bar_chart(figure, 
                                                     groups=age_group, 
                                                     year=year)
    else:
        fig = create_population_structure_bar_chart(figure, 
                                                 geos=[datum['location'] for datum in selected_data['points']], 
                                                 groups=age_group, 
                                                 year=year)
    return fig

@app.callback(
    Output("pop_graph", "figure"),
    [Input("center_map", "selectedData"), Input('year_slider', 'value')],
    [State("pop_graph", "figure")]
)
def update_pop_graph(selected_data, year, figure):
    year = str(year)
    if selected_data is None:
        fig = create_population_line_plot(figure, year=str(year))
    else:
        fig = create_population_line_plot(figure, 
                                       geos=[datum['location'] for datum in selected_data['points']], 
                                       year=year)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=True)

