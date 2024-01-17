from bs4 import BeautifulSoup
import requests
import csv

countries = [
    "BE",
    "BG",
    "DK",
    "DE",
    "EE",
    "FI",
    "FR",
    "GR",
    "IE",
    "IT",
    "HR",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "AT",
    "PL",
    "PT",
    "RO",
    "SE",
    "SK",
    "SI",
    "ES",
    "CZ",
    "HU",
    "CY"
]

def extract_nuts_names(country):
    print(f"Extracting NUTS names for {country}")
    url = f"https://de.wikipedia.org/wiki/NUTS:{country}"
    
    response = requests.get(url)
    html_code = response.text
    soup = BeautifulSoup(html_code, 'html.parser')

    tables = soup.find_all('table')

    nuts1_data = []
    nuts2_data = []
    nuts3_data = []

    for table in tables:
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            columns = row.find_all(['td', 'th'])
            if len(columns) == 6:  # Make sure it's a row with NUTS3 information
                nuts1_name = columns[0].text.strip()
                nuts1_id = columns[1].text.strip()
                nuts2_name = columns[2].text.strip()
                nuts2_id = columns[3].text.strip()
                nuts3_id = columns[4].text.strip()
                region_name = columns[5].text.strip()

                nuts1_data.append({'nuts': nuts1_id, 'name': nuts1_name})
                nuts2_data.append({'nuts': nuts2_id, 'name': nuts2_name})
                nuts3_data.append({'nuts': nuts3_id, 'name': region_name})
    return nuts1_data, nuts2_data, nuts3_data

nuts1_total = []
nuts2_total = []
nuts3_total = []

for country in countries:
    nuts1, nuts2, nuts3 = extract_nuts_names(country)
    nuts1_total.extend(nuts1)
    nuts2_total.extend(nuts2)
    nuts3_total.extend(nuts3)


with open(f'geo/names/nuts1_names.csv', 'w+', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['nuts', 'name'])
    writer.writerows([(item['nuts'], item['name']) for item in nuts1_total])

# Write nuts2 data to CSV
with open(f'geo/names/nuts2_names.csv', 'w+', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['nuts', 'name'])
    writer.writerows([(item['nuts'], item['name']) for item in nuts2_total])

# Write nuts3 data to CSV
with open(f'geo/names/nuts3_names.csv', 'w+', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['nuts', 'name'])
    writer.writerows([(item['nuts'], item['name']) for item in nuts3_total])

with open("geo/names/nuts_names.csv", 'w+') as file:
    writer = csv.writer(file)
    writer.writerow(['nuts', 'name'])
    writer.writerows([(item['nuts'], item['name']) for item in nuts1_total])
    writer.writerows([(item['nuts'], item['name']) for item in nuts2_total])
    writer.writerows([(item['nuts'], item['name']) for item in nuts3_total])