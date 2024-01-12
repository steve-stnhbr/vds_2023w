import pandas as pd

def to_numeric(df, columns=None):
    if columns is None:
        columns = get_years(df)
    df[columns] = df[columns].apply(pd.to_numeric, errors='coerce')
    return df

def to_numeric_bfill(df, columns=None):
    if columns is None:
        columns = get_years(df)
    df[columns] = df[columns].apply(pd.to_numeric, errors='coerce').bfill(axis=0)
    return df

def sort_to_numeric_bfill(df, columns=None, reverse=False):
    if columns is None:
        columns = get_years(df)
    sorted_columns = sorted(columns, reverse=reverse)
    df = df[[col for col in df.columns if col not in sorted_columns] + sorted_columns]
    df[columns] = df[columns].apply(pd.to_numeric, errors='coerce').bfill(axis=0)
    return df

def sort_to_numeric(df, columns=None, reverse=False):
    if columns is None:
        columns = get_years(df)
    sorted_columns = sorted(columns, reverse=reverse)
    df = df[[col for col in df.columns if col not in sorted_columns] + sorted_columns]
    df[columns] = df[columns].apply(pd.to_numeric, errors='coerce')
    return df

def get_years(df):
    return [col for col in df.columns if col.isdigit()]

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

def outersection(lst1, lst2):
    return list(set(lst1) | set(lst2))

def left_intersect(lst1, lst2):
    return list(set(lst1) - set(lst2))