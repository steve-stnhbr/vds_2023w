import os

ROOT_DIR = os.getcwd() + "/"

class NoDataAvailableError(Exception):
    
    def __init__(self, message="No data available", year=None):
        if year is not None:
            message = f"No data available for {year}"
        self.message = message
        super().__init__(self.message)