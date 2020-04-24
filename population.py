
import requests
import pandas as pd
import json


var_list = ['NAME', 'DATE_CODE', 'POP', 'DENSITY']
var_string = ",".join(var_list)
api = 'https://api.census.gov/data/2019/pep/population'
for_clause = 'county:*'
in_clause = 'state:53'
key_value = 'Your Key Value'
payload = {'get':var_string, 'for':for_clause, 'in':in_clause, 'key':key_value}
response = requests.get(api, payload)

if response.status_code == 200:
    print('\nThe request succeeded')
else:
    print(response.status_code)
    print(response.text)
    assert False

row_list = response.json()

colnames = row_list[0]
datarows = row_list[1:]
pop = pd.DataFrame(columns=colnames, data=datarows)
pop.set_index(var_list, inplace=True)
popfilename = '53_census-pop-data.csv'
pop.to_csv(popfilename)
