import json
from urllib.request import urlopen

AVAILABLE_YEARS = [2021, 2016, 2013, 2010, 2006]
AVAILABLE_RESOLUTIONS = ["60M", "20M", "10M", "03M"]
            
def query_to_file(url, filename):
    print(f"Querying {url}")
    try:
        with urlopen(url) as response:
            nuts = json.load(response)
    except:
        print(f"Failed to query {url}")
        return
    with open(filename, "w") as geo_file:
        json.dump(nuts, geo_file)

for year in AVAILABLE_YEARS:
    for resolution in AVAILABLE_RESOLUTIONS:
        query_to_file(
            f"https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_{resolution}_{year}_4326.geojson",
            f"geo/nuts_{resolution}_{year}.json"
        )

        for level in range(0,4):
            url = f"https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_{resolution}_{year}_4326_LEVL_{level}.geojson"
            filename = f"geo/nuts{level}_{resolution}_{year}.json"
            query_to_file(url, filename)