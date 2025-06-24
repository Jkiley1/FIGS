import datetime
import pandas as pd
df = pd.read_csv(r'C:\Users\josep\OneDrive\Desktop\Coding_env\mclen.csv')
# df.columns = df.iloc[0]
df = df.loc[:, df.columns[0]:df.columns[4]]
df.columns = ['Date', 'Advances', 'Declines', 'Up Volume', 'Down Volume']
df.set_index('Date', inplace=True)
df.index = pd.to_datetime(df.index, format="%M-%D-%Y-%H-%S")
print(df)