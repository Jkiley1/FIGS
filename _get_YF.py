import yfinance as yf
from playwright.async_api import async_playwright
import asyncio
import pandas as pd

ticker = yf.Ticker('AAPL')
hist = ticker.history(period='6mo')
hist.to_csv('yreax.csv')