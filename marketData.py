import numpy as np
import pandas as pd
from typing import Callable, Optional
# create a 10‑day date index
dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
import time
# example prices for three stocks over those 10 days
df = pd.DataFrame({
	"SPY": [499.65,506.78,503.53,500.55,499.52,495.16,499.72,505.65,505.41,503.49], #43.552
	"StockB": [200.0, 199.8, 200.5, 201.0, 200.7, 201.2, 202.0, 201.5, 202.3, 203.0],
	"StockC": [300.0, 301.2, 302.5, 302.0, 303.1, 304.0, 305.2, 305.0, 306.5, 307.0]
}, index=dates)

import subprocess
def process_exists(process_name): 
    call = 'TASKLIST', '/FI', f'imagename eq {process_name}'
    output = subprocess.check_output(call).decode()
    last_line = output.strip().split('\r\n')[-1]
    return last_line.lower().startswith(process_name.lower())


class MarketData():

	def __init__(self):
		pass


	from _get_IB import IBApp
	def establish_connection(paper: bool = True):
		"""_summary_

		Args:
			paper (bool, optional): Use a paper trade account. 
			Trading functionality will throw an error. Defaults to True.
		"""
		if process_exists('ibgateway.exe'):
			port = 4001
			if paper:
				port = port + 1
			app.connect("127.0.0.1", port, clientId=0)

		elif process_exists('tws.exe'):
			port = 7496
			if paper:
				port = port + 1
			app.connect("127.0.0.1", port, clientId=0)


def timing_decorator(func): 
		def wrapper(*args, **kwargs):
			start_time = time.time()
			result = func(*args, **kwargs)
			end_time = time.time()
			elapsed_time = end_time - start_time
			print(f"Function '{func.__name__}' executed in {elapsed_time:.6f} seconds")
			return result
		return wrapper

@timing_decorator
def relative_strength(tickers: list[str] | tuple[str] | str, n = 4) -> pd.DataFrame:
	"""_summary_

		Modifies a Dataframe with appended column showing the Relative Strength Index
		for a given asset price history.

	Args:
		tickers (list[str] | tuple[str] | str): 
		n (int, optional): _description_. Defaults to 14.

	Returns:
		DataFrame
	"""
	def _calculate_percentage_change(ticker):
		df[f'_%{ticker}'] = df[f'{ticker}'].pct_change()
		df[f'_+{ticker}'] = df[f'_%{ticker}'].where(df[f'_%{ticker}'] > 0, 0)
		df[f'_-{ticker}'] = df[f'_%{ticker}'].where(df[f'_%{ticker}'] < 0, 0)
		df[f'_++{ticker}'] = df[f'_+{ticker}'].rolling(n).mean()
		df[f'_--{ticker}'] = df[f'_-{ticker}'].rolling(n).mean()
		df.drop(df.index[0], inplace=True)
		print(df)
		df2 = df.loc[:, ~df.columns.str.startswith('_')]

	if isinstance(tickers, list|tuple):
		for ticker in tickers:
			_calculate_percentage_change(ticker=ticker)
	else: 
		_calculate_percentage_change(ticker=tickers)

relative_strength(['SPY'])
# Calculate RSI for periods n, where n = 14


"""https://www.cboe.com/us/futures/market_statistics/historical_data/
https://www.cboe.com/us/futures/market_statistics/historical_data/
https://www.cboe.com/us/futures/market_statistics/historical_data/
https://www.cboe.com/us/futures/market_statistics/historical_data/"""

# 1. Compute Period Changes
# 2. Find gains and losses
# 3. For gain, loss find average gain, loss for the first 14 periods
# 4. For i > 14, ((averageGain/Loss[i-1] * n-1) + Gain/Loss[i])/n
# 5. RS[i] = AvgGain[i]/AvgLoss[i]
# 6. RSI[i] = 100 - 100/1 + RS[i]