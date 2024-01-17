import pandas as pd
from .transformations import *
from .geojson import *
from .util import *

NUTS_PROPS_KEYS = ["NUTS_ID", "LEVL_CODE", "CNTR_CODE", "NUTS_NAME", "NAME_LATN", "MOUNT_TYPE", "URBN_TYPE", "FID", "area"]
NUTS_PROPS_COLUMS = ['id', 'level', 'country', 'name', 'name_latin', 'mountainous_type', 'urban_type', 'fid', 'area']

df_geo = pd.DataFrame([[(feature['properties'][key] if key in feature['properties'] else '-') for key in NUTS_PROPS_KEYS] for feature in current_geojson['features']], columns=NUTS_PROPS_COLUMS)

df_geo_names = pd.read_csv(ROOT_DIR + '/geo/names/nuts_names.csv', sep=';')

def aggregate_groups(df, groupby, columns=None, aggregate='sum', aggregate_others='first', reset_index=True) -> pd.DataFrame:
    if columns is None:
        columns = get_years(df)
    df = df.groupby(groupby).agg(
        {column: aggregate if column in columns else aggregate_others for column in df.columns}
    )
    if reset_index:
        df = df.reset_index(drop=True)
    return df

def assign_urbanization_type(df, geo_column="geo", as_string=True):
    df = pd.merge(df, df_geo[['id', 'urban_type']], left_on=geo_column, right_on='id').drop(['id'], axis=1)
    if as_string:
        df['urban_type'] = df['urban_type'].map(URBAN_TYPES.get)
    return df

def aggregate_by_geo_prop(df,
                          df_geo_column='geo',
                          geo_prop='urban_type',
                          years=None,
                          aggregate_years='sum',
                          aggregate_others='first',
                          reset_index=True,
                          level=None,
                          drop_unavailable=True) -> pd.DataFrame:
    if years is None:
        years = get_years(df)
    df_geo_lvl = df_geo.copy()
    if level is not None:
        df_geo_lvl = df_geo_lvl[df_geo['level'] == level]
    df_ut = pd.merge(df, df_geo_lvl[['id', geo_prop]], left_on=df_geo_column, right_on='id').drop(['id'], axis=1)
    df_ut = aggregate_groups(df_ut, groupby=[geo_prop], columns=years, aggregate=aggregate_years,
                             aggregate_others=aggregate_others, reset_index=reset_index)
    if drop_unavailable:
        df_ut = df_ut[~df_ut[geo_prop].isin(['-', '0'])]
    if reset_index:
        df_ut = df_ut.reset_index(drop=True)
    return df_ut

def get_geos_with_urban_types(urban_types):
    if isinstance(urban_types, str):
        urban_types = [urban_types]
    if isinstance(urban_types[0], str):
        urban_types = [list(URBAN_TYPES.values()).index(urban_type) for urban_type in urban_types]
    return df_geo[df_geo['urban_type'].isin(urban_types)]['id']

def get_geo_name(geo):
    values = df_geo_names[df_geo_names['nuts'] == geo]['name'].values
    return values[0] if len(values) > 0 else geo

def get_geo_names(geos):
    return df_geo_names[df_geo_names['nuts'].isin(geos)]['name'].values

def get_urban_types_of_geos(geos, as_string=True, unique=True):
    if as_string:
        urban_types = df_geo[df_geo['id'].isin(geos)]['urban_type'].map(URBAN_TYPES.get)
        if unique:
            return urban_types.unique()
        return urban_types
    urban_types = df_geo[df_geo['id'].isin(geos)]['urban_type']
    if unique:
        return urban_types.unique()
    return urban_types

def geo_is_level(geo, level=3):
    return len(geo) == 2 + level
