import sys
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import difflib
import json
import re
## to remove letters from a string: clean = re.sub('[^0-9]', '', i)

def fx_forwards(borrow, lend, t):
    from math import e
    rf = borrow - lend
    f = 100 * e ** (abs(rf)*t)
    print(f-100)


class StockData():
    def __init__(self) -> None:
        # Default response will be to use annual values
        self.annual = True
        self.yf_df = None
        file = json.load(open('C:\\Users\\josep\\OneDrive\\Desktop\\Coding_env\\words.json'))
     
        self.df = pd.DataFrame(data=[
                [fact, key['val'], key.get('start'), key.get('end'), re.sub('[^0-9]', '', key.get('frame'))]
                for accounting_convention in file['facts']
                for fact in file['facts'][accounting_convention]
                for unit in file['facts'][accounting_convention][fact]['units']
                for key in file['facts'][accounting_convention][fact]['units'][unit]
                if key.get('frame')
         ],
            columns=['Label', 'Value', 'Start', 'End', 'Frame'])
        
        # Only annual values
        self.annual_df = self.df[self.df['Frame'].str.len() == 4]

        # Only quarterly values
        self.quarterly_df = self.df[self.df['Frame'].str.len() > 4]
        
        self.labels = self.df['Label'].unique()
     

    def _get_keyword_finder(self, find = 'earnings'):
        cutoff = 1
        match = difflib.get_close_matches(find, self.labels, 1, cutoff=cutoff)
        while len(match) == 0:
            cutoff -= 0.05
    
        return match
    def different_function(self, annual):
        self.annual = annual




#start_date = dt.datetime.strptime(start, "%Y-%m-%d",)
#end_date = dt.datetime.strptime(end, "%Y-%m-%d")


import yfinance as yf # type: ignore


def price_history(tickers: list, _equal_start = True, _indexed_values = False):
    """
    If there is only one ticker, we can plot the price
    If there is more than one ticker, we can index to 100
    If more than one and start at different times
        CANCEL: We can either index the new stocks to the old
            CANCEL: ones at the time they enter
        We can find the date when all stocks are
            trading and make all stocks == 100 at that t
    
    Maybe we can find this by dropping all NaN on a copy of df
    and finding df.index[0]
    """
    df = yf.download(tickers=tickers, group_by='Ticker')
    if _equal_start == True: 
        df = df.loc[df.index > df.apply(pd.Series.first_valid_index).max()]
        
    print(df[('QQQ', 'Open')])
    

        
   

#df['Date'] = pd.to_datetime(df.index).tz_localize(None)
