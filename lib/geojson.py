import json
from geojson_rewind import rewind
from shapely.geometry import shape
from urllib.request import urlopen
import pandas as pd
import functools
import numpy as np

AVAILABLE_YEARS = [2021, 2016, 2013, 2010, 2006]
AVAILABLE_RESOLUTIONS = ["60M", "20M", "10M", "03M"]

URBAN_TYPES = {
    0: "unavailable",
    1: "urban",
    2: "intermediate",
    3: "rural",
}

MOUNTAIN_AREAS = {
    0: "unavailable",
    1: "> 50% of population lives in mountain areas",
    2: "> 50 % of surface in mountain areas",
    3: "> 50 % of surface in mountain areas and > 50% of population lives in mountain areas",
    4: "non-mountain region"
}

current_geojson = None

def get_most_recent_year(year):
    # return the most recent year that is available
    for available_year in AVAILABLE_YEARS:
        if year >= available_year:
            return available_year
    return AVAILABLE_YEARS[-1]

def get_nuts_geojson0(level, year):
    url = f"https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_20M_{get_most_recent_year(year)}_3035.geojson"
    #url = f"https://raw.githubusercontent.com/eurostat/Nuts2json/master/pub/v2/{get_most_recent_year(year)}/3035/20M/nutsrg_{level}.json"
    #url = f"https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/eurostat/ew/nuts{level}.json"
    #url = "https://datahub.io/core/geo-nuts-administrative-boundaries/r/nuts_rg_60m_2013_lvl_2.geojson"
    #url = "https://data-osi.opendata.arcgis.com/datasets/5abac930b4b64faca220d6a2dcd6d7fc_0.geojson?outSR=%7B%22latestWkid%22%3A2157%2C%22wkid%22%3A2157%7D"
    with urlopen(url) as response:
        nuts = load_geo(response)
    return nuts

@functools.lru_cache()
def get_nuts_geojson(level, year):
    for resolution in AVAILABLE_RESOLUTIONS:
        try:
            filename = f"geo/nuts{level}_{resolution}_{get_most_recent_year(year)}.json"
            nuts = load_geojson(filename)
        except FileNotFoundError:
            print(f"Failed to find geojson for {resolution} {get_most_recent_year(year)}")
            #filename = f"geo/nuts_{resolution}_{get_most_recent_year(year)}.json"
        global current_geojson
        current_geojson = nuts
        return nuts
def load_geojson(filename):
    with open(filename) as geo_file:
        nuts = load_geo(geo_file)
    return nuts


def load_geo(json_content):
    geo = rewind(json.load(json_content))
    data = []
    for feature in geo['features']:
        s = shape(feature["geometry"])
        feature['properties']['area'] = s.area
        feature['properties']['bounds'] = s.bounds
        feature['properties']['center'] = {"x": s.centroid.x, "y": s.centroid.y}
    return geo

def get_zoom_center(locations):
    global current_geojson
    max_lat = -180
    max_lng = -180
    min_lat = 180
    min_lng = 180
    found = 0
    # select the feature that contains the location
    for feature in current_geojson['features']:
        if feature['id'] in locations:
            found = found + 1
            bounds = feature['properties']['bounds']
            max_lat = max(max_lat, bounds[3])
            max_lng = max(max_lng, bounds[2])
            min_lat = min(min_lat, bounds[1])
            min_lng = min(min_lng, bounds[0])
        if found >= len(locations):
            break
    # calculate the center of the selected features
    center_lat = (max_lat + min_lat) / 2
    center_lng = (max_lng + min_lng) / 2
    # calculate the zoom level
    max_bound = max(abs(max_lat-min_lat), abs(max_lng-min_lng)) * 111
    zoom = 11.5 - np.log(max_bound)
    return zoom, {"lat": center_lat, "lon": center_lng}