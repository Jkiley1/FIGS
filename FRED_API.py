_fred_key='84bbb2a4c3682b3cc6f6c1301de7a909'
import json
import time
import requests
import pandas as pd
import sqlite3 as sql
_fred_file = r'C:\Users\josep\OneDrive\Desktop\Coding_env\FinancialProject\FRED.json'
def timing_decorator(func):
		def wrapper(*args, **kwargs):
			start_time = time.time()
			result = func(*args, **kwargs)
			end_time = time.time()
			elapsed_time = end_time - start_time
			print(f"Function '{func.__name__}' executed in {elapsed_time:.6f} seconds")
			return result
		return wrapper

# https://api.stlouisfed.org/fred/category/children?category_id=2&api_key=84bbb2a4c3682b3cc6f6c1301de7a909&file_type=json
# data is here: https://api.stlouisfed.org/fred/series/observations?series_id=GNPCA&api_key=84bbb2a4c3682b3cc6f6c1301de7a909&date=2020-05-01&file_type=json
@timing_decorator
def tags() -> list:
    response = requests.get(f'https://api.stlouisfed.org/fred/tags?api_key=84bbb2a4c3682b3cc6f6c1301de7a909&file_type=json')
    if response.status_code == 200:
        parsed_json = response.json()
        df = pd.DataFrame(parsed_json['tags'])
        df = df.set_index('group_id')
        return df['name'].unique()
@timing_decorator
def tags_to_series_names():
    seriess = []
    for name in tags():
        response = requests.get(f'https://api.stlouisfed.org/fred/tags/series?tag_names={name}&api_key=84bbb2a4c3682b3cc6f6c1301de7a909&file_type=json')
        json_response = response.json()['seriess']
        for _dict in json_response:
            seriess.append([name,
                        _dict.get('id'),
                        _dict.get('title'),
                        _dict.get('observation_start'),
                        _dict.get('observation_end'),
                        _dict.get('last_updated'),
                        _dict.get('frequency'),
                        _dict.get('units'),
                        _dict.get('seasonal_adjustment_short'),
                        _dict.get('popularity'),
                        _dict.get('group_popularity')])
    df = pd.DataFrame(seriess, columns=['name', 'id', 'title', 'start', 'end', 'updated', 'freq', 'units', 'seasonal', 'popularity', 'group_popularity'])
    df = df[~df['title'].str.contains('DISCONTINUED')]
    df.to_csv('third_fred_eral.csv')
def remove_duplicates():
    df = pd.read_csv(r"C:\Users\josep\OneDrive\Desktop\Coding_env\first_fred.csv")
    print(df.shape)
    df = df.drop_duplicates(subset=['title'], keep='first')
    print(df.shape)
    df = df[~df['title'].str.contains('DISCONTINUED')]
    print(df.shape)
    df.to_csv('fred_no_dupes.csv')

def get_fred():
    """ Gets data from FRED using the tags
        this need to find
    """
    response = requests.get('https://api.stlouisfed.org/fred/series/observations?series_id=CDSP&api_key=84bbb2a4c3682b3cc6f6c1301de7a909&file_type=json')
    source = response.json()['observations']

    series = [[observation.get('date'), observation.get('value')] for observation in source]
    df = pd.DataFrame(series, columns=['date', 'value'])
    df.set_index('date', inplace=True)
    df.to_csv('fred_read_me.csv')
    print(df)
import csv
@timing_decorator
def sql_trial():
    conn = sql.connect(":memory:")
    cur = conn.cursor()
    cur.execute("CREATE TABLE records (name TEXT, value FLOAT)")
    with open("fred_no_dupes.csv") as file:
        reader = csv.reader(file)
        cur.executemany("INSERT INTO records VALUES (?,?)", reader)
    for row in cur.execute("SELECT name, AVG(value) FROM records GROUP BY name"):
          print(row)
df = pd.read_csv("fred_no_dupes.csv")
df.set_index('units', inplace=True)
df = df.loc[:, ~df.columns.str.contains(":")]
print(df.columns)
df.to_csv("fred_no_dupes.csv")
