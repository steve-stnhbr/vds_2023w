import os
from collections import Counter

ROOT_DIR = os.getcwd() + "/"

class NoDataAvailableError(Exception):
    
    def __init__(self, message="No data available", year=None):
        if year is not None:
            message = f"No data available for {year}"
        self.message = message
        super().__init__(self.message)

def extract_selected(map_hover, hovers, id, checkkeys=[], checkarray=[]):
    selected = [datum['location'] for datum in (map_hover['points'])] if map_hover is not None else []
    for hover, array, key in zip(hovers, checkarray, checkkeys):
        if hover is not None:
            selected = selected + ([datum[key or 'id'] 
                                    for datum in hover['points'] 
                                        if (id in datum['custom_data'] 
                                            if array 
                                            else datum['custom_data'] == id)] 
                                    if hover is not None 
                                    else []
                                    )
    return selected

def extract_geos(selected_data):
    return [datum['location'] for datum in selected_data['points']] if selected_data is not None else []

def list_equals(list1, list2):
    if len(list1) != len(list2):
        return False
    
    for item1, item2 in zip(list1, list2):
        if isinstance(item1, list) and isinstance(item2, list):
            if not list_equals(item1, item2):
                return False
        elif item1 != item2:
            return False
    
    return True