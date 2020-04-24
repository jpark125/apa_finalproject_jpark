import requests
import pandas as pd
import json


var_info = pd.read_csv('census-variables.csv')
var_name = var_info['variable'].to_list()
var_list = ['NAME'] + var_name
var_string = ",".join(var_list)
print(var_string)
api = 'https://api.census.gov/data/2018/acs/acs5'
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
attain = pd.DataFrame(columns=colnames, data=datarows)
attain.set_index('NAME', inplace=True)
attain.to_csv('53_census-data.csv')

pd.set_option('display.max_rows', None)
var_info = pd.read_csv('census-variables.csv', index_col='variable')
var_group = var_info['group']


attain = pd.read_csv('53_census-data.csv', index_col='NAME')
group_by_level = attain.groupby(var_group, axis='columns', sort=False)
by_level = group_by_level.sum()
levels =['<hs', 'hs', 'some col', 'ba', 'grad']
by_level['check'] = by_level[levels].sum(axis='columns')


pct = 100*by_level.div(by_level['total'], axis='index')


lo = pct['<hs'] + pct['hs']
hi = pct['ba'] + pct['grad']
ratio = round(hi/lo, 2)
attain['ratio'] = ratio
edufilename = '53_edu_attainment.csv'
attain.to_csv(edufilename)
