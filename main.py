import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, State
import os
import flask
import plotly.io as pio
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from map import *
from pop_structure import *
from pop import *
from births_deaths import *
from sex import *

from lib.util import *

HEADING = "Differences between urban and rural areas in the EU"
DEFAULT_GRAPH_STYLE = {"height": "80vh"}
DEFAULT_GRAPH_LAYOUT = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

#pio.templates.default = "plotly_dark"

css_directory = os.getcwd()
stylesheets = ['style.css']
static_css_route = '/static/'
external_stylesheets = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"] + [os.path.join(static_css_route, stylesheet) for stylesheet in stylesheets]
external_scripts = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"]

app = Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
server = app.server

@app.server.route('{}<stylesheet>'.format(static_css_route))
def serve_stylesheet(stylesheet):
    if stylesheet not in stylesheets:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(
                stylesheet
            )
        )
    return flask.send_from_directory(css_directory, stylesheet)

app.layout = html.Div([
    html.H1(HEADING),
    html.Div([], id="empty"),
    html.Div([
        html.H2("Year"),
        dcc.Slider(step=None, marks={year: str(year) for year in years_population_density}, id='year_slider', value=int(years_population_density[-1])),
    ]),
    html.Div([
        html.Div([
            html.H2("Population Density by NUTS3 Region", id="map_heading"),
            dcc.Graph(
                id="center_map", 
                figure=create_map_graph(None, level=3), 
                clear_on_unhover=True,
            ),
            html.Div([
                html.Div([
                    dmc.Switch(
                        size="md",
                        radius="xl",
                        label="Show Population Density",
                        checked=True,
                        id="pop_density_switch"
                    ),
                ], className="col"),
                html.Div([
                    dmc.Switch(
                        size="md",
                        radius="xl",
                        label="Show Urban Types",
                        checked=True,
                        id="urban_type_switch"
                    ),
                ], className="col"),
                html.Div([
                    dcc.Dropdown(
                        options=[{'label': row['country_name'], 'value': row['country_code']} for _, row in df_geo_names.groupby('country_code', as_index=False, sort=False).apply(lambda x: x.iloc[0]).iterrows()],
                        id="country_select", 
                        multi=True,
                        placeholder="Select countries",
                    ),
                ], className="col"),
                html.Button("debug", id="debug_button", style={"display": "none"}),
            ], className="pt-3 row display-flex justify-content-center"),
        ], className="col-7", id="map_div"),
        html.Div([
            html.H2("Age Distribution by Region", id="pop_distr_heading"),
            dcc.Dropdown(
                id="age_group_select", 
                options=[{"label": group, "value": group} for group in POP_AGE_GROUPS.keys()], 
                value="fine"
            ),
            html.Div([
                dcc.Graph(
                    id="pop_distr_graph", 
                    figure=create_population_structure_bar_chart(None),
                    clear_on_unhover=True,
                ),
                html.Div([
                    html.H3("No data available")
                ], id="pop_distr_alert", style={"display": "none"}, className="alert")
            ], className="alert-container")
        ], className="col", id="pop_distr_div"),
        
    ], className="row flex-nowrap", id="graphs1_div"),
    html.Div([
        html.Div([
            html.H2("Population", id="pop_heading"),
            html.Div([
                dcc.Graph(
                    id="pop_graph",
                    figure=create_population_line_plot(None), 
                    clear_on_unhover=True,
                ),
                html.Div([
                    html.H3("No data available")
                ], id="pop_alert", style={"display": "none"}, className="alert")
            ], className="alert-container")
        ], className="col", id="pop_div"),
        html.Div([
            html.H2("Births and Deaths", id="births_deaths_heading"),
            html.Div([
                dmc.RadioGroup(
                    [dmc.Radio(l, value=k) for l, k in {"total": 'total', "per capita": 'pc'}.items()],
                    id="births_deaths_radio",
                    value="total",
                    size="sm",
                    mb=-35,
                    style={'position': 'relative', 'z-index': '5'}
                ),
                dcc.Graph(
                    id="births_deaths_graph",
                    figure=create_births_deaths_line_plot(None), 
                    clear_on_unhover=True,
                ),
                html.Div([
                    html.H3("No data available")
                ], id="births_deaths_alert", style={"display": "none"}, className="alert")
            ], className="alert-container")
        ], className="col", id="births_deaths_div"),
        html.Div([
            html.H2("Sex by Age Group", id="sex_distr_heading"),
            html.Div([
                dcc.Graph(
                    id="sex_distr_graph",
                    figure=create_sex_violin_plot(None), 
                    clear_on_unhover=True,
                ),
                html.Div([
                    html.H3("No data available")
                ], id="sex_distr_alert", style={"display": "none"}, className="alert")
            ], className="alert-container")
        ], className="col", id="sex_distr_div"),
    ], className="row flex-nowrap", id="graphs2_div"),
], id="main_div", className="")


@app.callback(
    Output("center_map", "figure"),
    [
        Input('year_slider', 'value'), 
        Input('pop_distr_graph', 'hoverData'),
        Input('sex_distr_graph', 'hoverData'),
        Input("center_map", "selectedData"),
        Input("debug_button", "n_clicks"),
        Input("pop_density_switch", "checked"),
        Input("urban_type_switch", "checked"),
    ],
    [State("center_map", "figure")],
)
def update_map(year, pop_distr_hover, sex_distr_hover, map_selection, _, show_pop_density, show_urban_type, figure):
    highlighted = []
    highlighted = highlighted + ([datum['id'] for datum in (pop_distr_hover['points'])] if pop_distr_hover is not None else [])
    highlighted = highlighted + ([datum['x'] for datum in sex_distr_hover['points']] if sex_distr_hover is not None else [])
    map_selected_locations = [datum['location'] for datum in (map_selection['points'])] if map_selection is not None else []
    return create_map_graph(
        figure, 
        highlight_locations=highlighted, 
        level=3, 
        year=year, 
        selected_data=map_selected_locations,
        color_population_density=show_pop_density,
        color_urban_types=show_urban_type
    )
    
@app.callback(
    [
        Output("pop_distr_graph", "figure"),
        Output("pop_distr_alert", "style")
    ],
    [
        Input("center_map", "selectedData"), 
        Input('age_group_select', 'value'), 
        Input('year_slider', 'value'),
        Input("center_map", "hoverData"),
        Input("sex_distr_graph", "hoverData")
    ],
    [State("pop_distr_graph", "figure")]
)
def update_pop_distr_grap(selected_data, age_group, year, map_hover, sex_distr_hover, figure):
    try:
        selected = [datum['location'] for datum in (map_hover['points'])] if map_hover is not None else []
        selected = selected + ([datum['x'] for datum in sex_distr_hover['points']] if sex_distr_hover is not None else [])
    
        year = str(year)
        if selected_data is None:
            fig = create_population_structure_bar_chart(figure, 
                                                        groups=age_group, 
                                                        year=year, 
                                                        selected=selected)
        else:
            fig = create_population_structure_bar_chart(figure, 
                                                    geos=[datum['location'] for datum in selected_data['points']], 
                                                    groups=age_group, 
                                                    year=year,
                                                    selected=selected)
        return (fig, {"display": "none"})
    except NoDataAvailableError:
        return (figure, {"display": "block"})

@app.callback(
    [Output("pop_graph", "figure"),
     Output("pop_alert", "style")],
    [
        Input("center_map", "selectedData"), 
        Input('year_slider', 'value'),
        Input("center_map", "hoverData"),
        Input("pop_distr_graph", "hoverData"),
        Input("sex_distr_graph", "hoverData")
    ],
    [State("pop_graph", "figure")]
)
def update_pop_graph(selected_data, year, map_hover, pop_distr_hover, sex_distr_hover, figure):
    try:
        selected = [datum['location'] for datum in (map_hover['points'])] if map_hover is not None else []
        selected = selected + ([datum['id'] for datum in (pop_distr_hover['points'])] if pop_distr_hover is not None else [])
        selected = selected + ([datum['x'] for datum in sex_distr_hover['points']] if sex_distr_hover is not None else [])
    
        year = str(year)
        if selected_data is None:
            fig = create_population_line_plot(figure, 
                                            year=str(year), 
                                            selected=selected)
        else:
            fig = create_population_line_plot(figure, 
                                            geos=[datum['location'] for datum in selected_data['points']], 
                                            year=year,
                                            selected=selected)
        return (fig, {"display": "none"})
    except NoDataAvailableError:
        return (figure, {"display": "block"})
    
@app.callback(
    [Output("births_deaths_graph", "figure"),
     Output("births_deaths_alert", "style")],
    [
        Input("center_map", "selectedData"), 
        Input('year_slider', 'value'),
        Input("center_map", "hoverData"),
        Input("pop_distr_graph", "hoverData"),
        Input("sex_distr_graph", "hoverData"),
        Input("births_deaths_radio", "value"),
    ],
    [State("births_deaths_graph", "figure")]
)
def update_births_deaths_graph(selected_data, year, map_hover, pop_distr_hover, sex_distr_hover, unit, figure):
    try:
        selected = [datum['location'] for datum in (map_hover['points'])] if map_hover is not None else []
        selected = selected + ([datum['id'] for datum in (pop_distr_hover['points'])] if pop_distr_hover is not None else [])
        selected = selected + ([datum['x'] for datum in sex_distr_hover['points']] if sex_distr_hover is not None else [])
    
        year = str(year)
        if selected_data is None:
            fig = create_births_deaths_line_plot(figure, 
                                            year=str(year), 
                                            selected=selected,
                                            unit=unit)
        else:
            fig = create_births_deaths_line_plot(figure, 
                                            geos=[datum['location'] for datum in selected_data['points']], 
                                            year=year,
                                            selected=selected,
                                            unit=unit)
        return (fig, {"display": "none"})
    except NoDataAvailableError:
        return (figure, {"display": "block"})
    
@app.callback(
    [Output("sex_distr_graph", "figure"),
     Output("sex_distr_alert", "style")],
    [
        Input("center_map", "selectedData"), 
        Input('year_slider', 'value'),
        Input("center_map", "hoverData"),
        Input("pop_distr_graph", "hoverData"),
    ],
    [State("sex_distr_graph", "figure")]
)
def update_sex_distr_graph(selected_data, year, map_hover, pop_distr_hover, figure):
    try:
        selected = [datum['location'] for datum in (map_hover['points'])] if map_hover is not None else []
        selected = selected + ([datum['id'] for datum in (pop_distr_hover['points'])] if pop_distr_hover is not None else [])
        year = str(year)
        if selected_data is None:
            fig = create_sex_violin_plot(figure, 
                                            year=str(year), 
                                            selected=selected)
        else:
            fig = create_sex_violin_plot(figure, 
                                            geos=[datum['location'] for datum in selected_data['points']], 
                                            year=year,
                                            selected=selected)
        return (fig, {"display": "none"})
    except NoDataAvailableError:
        return (figure, {"display": "block"})
    
@app.callback(
    Output("empty", "children"),
    Input("year_slider", "value")
)
def load_geojson(year):
    get_nuts_geojson(3, year)
    return []

@app.callback(
    Output("center_map", "selectedData"),
    Input("country_select", "value")
)
def select_countries(countries):
    if countries is None or len(countries) == 0:
        return None
    return {"points": [{"location": geo} for geo in df_geo[df_geo['id'].str.startswith(tuple(countries))]['id']]}

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=True)

