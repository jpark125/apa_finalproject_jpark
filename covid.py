import pandas as pd
import csv
import io
import zipfile 
import seaborn as sns
import matplotlib.pyplot as plt

zipname = 'covid-19-data-master.zip'
csvname = 'us-counties.csv'

zip_object = zipfile.ZipFile(zipname)
inp_byte = zip_object.open(csvname)
inp_handle=io.TextIOWrapper(inp_byte)

covid = pd.read_csv(inp_handle, dtype=str)

#split the fips code into state and county for merge
(start, stop, step) = (0,2,1)
covid['fips']=covid['fips'].astype(str)
covid['fps_stt'] = covid['fips'].str.slice(start, stop, step)
covid['fps_cty'] = covid['fips'].str.slice(-3)


#split year, month, and day to sort
covid['month'] = covid['date'].str.slice(5,7)
month = covid['month']
(jan, feb, mar, apr) = ('01', '02','03','04')
covid.loc[month==jan, 'month_a'] = 'Jan'
covid.loc[month==feb, 'month_a'] = 'Feb'
covid.loc[month==mar, 'month_a'] = 'Mar'
covid.loc[month==apr, 'month_a'] = 'Apr'


# State Fipscode Dictionary Building
df = covid[['fps_stt', 'state']]
df = df.drop_duplicates(subset=None, keep='first', inplace=False)
df = df[df.fps_stt != 'na']
df.reset_index(drop=True, inplace=True)

df['state'] = df['state'].astype(str)
df['state'] = df['state'].str.lower()
state_fps = df.set_index('state')['fps_stt'].to_dict()
print(state_fps)


# Making a function for slicing the state data and sum up by months
def daily_by_state(state):
    fipscode = state_fps[state]
    a = '_covid19_daily.csv'
    filename = fipscode + a
    newdf = covid[covid['fps_stt']==fipscode]
    return newdf.to_csv(filename, header=True)

def monthly_by_county(state):
    fipscode = state_fps[state]
    a = '_covid19_daily.csv'
    filename = fipscode + a
    fh = pd.read_csv(filename)
    fh.sort_values(['county', 'date'], axis=0, ascending=True, inplace=True)
    grouped = fh.groupby(['county', 'fips', 'fps_stt', 'fps_cty', 'month_a'], sort=False)
    newfile = grouped[['cases', 'deaths']].sum()
    newname = fipscode + '_monthly_by_county.csv'
    return newfile.to_csv(newname, header=True)

statename='washington'
daily_by_state(statename)
monthly_by_county(statename)



#Total cases and deaths calculation
def total_cases_deaths(filename):
    df = pd.read_csv(filename)
    df['cases'] = df['cases'].astype(float)
    df['deaths'] = df['deaths'].astype(float)
    grouped = df.groupby(['county', 'fips', 'fps_cty'], sort=False, as_index=False)
    total_cases = grouped['cases'].transform(sum)
    total_deaths = grouped['deaths'].transform(sum)
    df['total_cases'] = total_cases
    df['total_deaths'] = total_deaths
    return df

filename = '53_monthly_by_county.csv'
newfilename = '53_covid19_total.csv'

state_covid = total_cases_deaths(filename)
state_covid.to_csv(newfilename)


#Merging with the population and the education data
pop_df = pd.read_csv('53_census-pop-data.csv')
pop_df = pop_df[pop_df['DATE_CODE']==12]
pop_df = pop_df[['county', 'POP', 'DENSITY']]

attain = pd.read_csv('53_edu_attainment.csv')

merged = attain.merge(state_covid, left_on='county', right_on='fps_cty', how='left', validate='1:m', indicator=True)
merged.drop('_merge', axis='columns', inplace=True)

covid_ed = merged[['county_y', 'fips', 'ratio', 'total_cases', 'total_deaths', 'fps_cty']]
covid_ed = covid_ed.drop_duplicates(subset=None, keep='first', inplace=False)
covid_ed = covid_ed.dropna()
covid_ed['fatality'] = round(covid_ed['total_deaths']/covid_ed['total_cases']*100, 2)
covid_ed = covid_ed.sort_values('ratio', ascending=False)
covid_ed['fips'] = covid_ed['fips'].astype('int64')
covid_ed['fps_cty'] = covid_ed['fps_cty'].astype('int64')
covid_ed = covid_ed[['county_y', 'fips', 'ratio', 'total_cases', 'total_deaths', 'fatality', 'fps_cty']]

covid_ed_pop = covid_ed.merge(pop_df, left_on='fps_cty', right_on='county', how='left', validate='1:m', indicator=True)
covid_ed_pop.drop(['fps_cty','_merge'], axis='columns', inplace=True)
covid_ed_pop['cases_per_pop'] = round(covid_ed_pop['total_cases']/covid_ed_pop['POP']*1000, 2)

finalfile = '53_edu_covid_pop.csv'
covid_ed_pop.to_csv(finalfile)

# Scatter plot analysis
test = pd.read_csv('13_edu_covid_pop.csv')

sns.regplot(x=covid_ed_pop['DENSITY'], y=covid_ed_pop['ratio'])
sns.regplot(x=covid_ed_pop['ratio'], y=covid_ed_pop['cases_per_pop'])
sns.regplot(x=covid_ed_pop['DENSITY'], y=covid_ed_pop['cases_per_pop'])
sns.regplot(x=covid_ed_pop['DENSITY'], y=covid_ed_pop['fatality'])
sns.regplot(x=covid_ed_pop['ratio'], y=covid_ed_pop['fatality'])
