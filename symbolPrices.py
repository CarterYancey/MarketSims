import yfinance as yf
import pandas as pd
import os
import sys, getopt
import numpy as np

pd.set_option("display.max_rows", None, "display.max_columns", None)
path = os.path.dirname(os.path.realpath(__file__))+'/'
file=''
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], 'hi:p:')
except getopt.GetoptError as err:
    print(str(err))
    print('SymbolPerformance.py -h for usage')
    sys.exit(2)
for opt, arg in opts:
    if opt in("-h", "--help"):
        print(' -i <input file> \t Filename of file that contains list of symbols seperated by newlines. Must be in same directory as this script, unless the -p flag is used.')
        print(' -p, --path=<directory> \t Directory for this script to work in. Working directory by default.')
        sys.exit(2)
    elif opt in ('-i', "--infile"):
        file = arg
    elif opt in ('-p', "--path"):
        path = arg+'/'
if (file==''):
    print('Must have input file. See SymbolPerformance.py -h for usage')
    sys.exit(2)

symbols = [line.rstrip('\n') for line in open(path+file)]
data_df = yf.download(tickers=symbols, period='1d', rounding='True')
data_df = data_df['Close']
name=file.split('.')[0]
data_df.transpose().to_csv(path+name+'_Prices.csv', index=True, header=True)
