import os
from collections import Counter
import threading
from threading import Timer

ROOT_DIR = os.getcwd() + "/"

class NoDataAvailableError(Exception):
    def __init__(self, message="No data available", year=None):
        if year is not None:
            message = f"No data available for {year}"
        self.message = message
        super().__init__(self.message)

def extract_selected(map_hover, hovers, id, checkkeys=[], checkarray=[]):
    selected = [datum['location'] for datum in (map_hover['points'])] if map_hover is not None else []
    for i, hover in enumerate(hovers):
        try:
            array = checkarray[i]
        except IndexError:
            array = False
        try:
            key = checkkeys[i]
        except IndexError:
            key = 'id'
        if hover is not None:
            for datum in hover['points']:
                add = False
                if array:
                    add = id in datum['customdata']
                else:
                    add = datum['customdata'] == id
                if add:
                    selected.append(datum[key])
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

def debounce1(wait_time):
    """
    Decorator that will debounce a function so that it is called after wait_time seconds
    If it is called multiple times, will wait for the last call to be debounced and run only this one.
    """

    def decorator(function):
        def debounced(*args, **kwargs):
            def call_function():
                debounced._timer = None
                return function(*args, **kwargs)
            # if we already have a call to the function currently waiting to be executed, reset the timer
            if debounced._timer is not None:
                debounced._timer.cancel()

            # after wait_time, call the function provided to the decorator with its arguments
            debounced._timer = threading.Timer(wait_time, call_function)
            debounced._timer.start()

        debounced._timer = None
        return debounced

    return decorator


def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                debounced.t.cancel()
            except(AttributeError):
                pass
            debounced.t = Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator