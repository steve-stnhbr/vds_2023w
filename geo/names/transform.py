import pandas as pd
import csv


df = pd.read_excel('geo/names/names_raw.xlsx', sheet_name='names')
df['country_code'] = df['Code 2021'].str[:2]
df_country = pd.read_csv('geo/country_codes.csv', usecols=['country_name', 'alpha-2'])

# merge country names by the first two letters of the NUTS code
df = pd.merge(df, df_country, left_on='country_code', right_on='alpha-2', how='left').drop(['alpha-2'], axis=1)

nuts1_array = []
nuts2_array = []
nuts3_array = []

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    code = row['Code 2021']
    
    # Check NUTS level 1
    if pd.notnull(row['NUTS level 1']):
        nuts1 = {'code': code, 'name': row['NUTS level 1'], 'country_name': row['country_name'], 'country_code': row['country_code']}
        nuts1_array.append(nuts1)
    
    # Check NUTS level 2
    if pd.notnull(row['NUTS level 2']):
        nuts2 = {'code': code, 'name': row['NUTS level 2'], 'country_name': row['country_name'], 'country_code': row['country_code']}
        nuts2_array.append(nuts2)

    # Check NUTS level 3
    if pd.notnull(row['NUTS level 3']):
        nuts3 = {'code': code, 'name': row['NUTS level 3'], 'country_name': row['country_name'], 'country_code': row['country_code']}
        nuts3_array.append(nuts3)
    
# Write nuts1 data to CSV
with open(f'geo/names/nuts1_names.csv', 'w+', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['nuts', 'name', 'country_name', 'country_code'])
    writer.writerows([(item['code'], item['name'], item['country_name'], item['country_code']) for item in nuts1_array])

# Write nuts2 data to CSV
with open(f'geo/names/nuts2_names.csv', 'w+', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['nuts', 'name', 'country_name', 'country_code'])
    writer.writerows([(item['code'], item['name'], item['country_name'], item['country_code']) for item in nuts2_array])

# Write nuts3 data to CSV
with open(f'geo/names/nuts3_names.csv', 'w+', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['nuts', 'name', 'country_name', 'country_code'])
    writer.writerows([(item['code'], item['name'], item['country_name'], item['country_code']) for item in nuts3_array])

# Write nuts data to CSV
with open(f'geo/names/nuts_names.csv', 'w+', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['nuts', 'name', 'country_name', 'country_code'])
    writer.writerows([(item['code'], item['name'], item['country_name'], item['country_code']) for item in nuts1_array])
    writer.writerows([(item['code'], item['name'], item['country_name'], item['country_code']) for item in nuts2_array])
    writer.writerows([(item['code'], item['name'], item['country_name'], item['country_code']) for item in nuts3_array])
