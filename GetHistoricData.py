import yfinance as yf
import pandas as pd
import sys

symbols = [line.rstrip('\n') for line in open("Dow30.txt")]
data_df = yf.download(tickers=symbols, period='max', interval='1d', rounding='True', actions=True, group_by="ticker")
for sym in symbols:
    data_df[sym].to_csv(sym+'.csv')

