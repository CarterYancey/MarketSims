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
data_df = yf.download(tickers=symbols, period='1y', interval='1d', rounding='True')
data_df = data_df['Close']
size = len(data_df)
#The following maps averages to the list of symbols
fifteenDayAVG = []
thirtyDayAVG = []
sixMonthAVG = []
priceTo15dma = [] #less than 1 means the share price is lower than its 15-day mean
priceTo30dma = [] #less than 1 means the share price is lower than its 30-day mean
priceTo180dma = [] #less than 1 means the share price is lower than its 180-day mean
shortTermBear = [] #True if the 15-day mean is under the 30-day mean
longTermBear = [] #True if the 15-day mean is under the 6-month mean
highestAverage = [] #30 day MA 15 days after highest TTM ticker price.
                    #^This close to 52-week high but flattens short-lived spikes

for sym in symbols:
    fifteenDayAVG.append(data_df[size-15:][sym].mean())
    thirtyDayAVG.append(data_df[size-30:][sym].mean())
    sixMonthAVG.append(data_df[size-180:][sym].mean())
    sharePrice = data_df[sym][size-1]
    priceTo15dma.append(sharePrice / fifteenDayAVG[-1])
    priceTo30dma.append(sharePrice / thirtyDayAVG[-1])
    priceTo180dma.append(sharePrice / sixMonthAVG[-1])
    shortTermBear.append(fifteenDayAVG[-1] / thirtyDayAVG[-1])
    longTermBear.append(fifteenDayAVG[-1] / sixMonthAVG[-1])
    high_index = np.argmax(data_df[:][sym])
    highestAverage.append(sharePrice/data_df[max(high_index-15,0):min(high_index+15, size-1)][sym].mean())
    #^Use max and min above to avoid cases where high is at the ends of the array

#Create dataframe from the information calculated above
results = {'Sale ratio': pd.Series(priceTo15dma, index=symbols),
           'Discount': pd.Series(priceTo30dma, index=symbols),
           'Dip': pd.Series(priceTo180dma, index=symbols),
	   'YoungBear': pd.Series(shortTermBear, index=symbols),
	   'OldBear': pd.Series(longTermBear, index=symbols),
           'High': pd.Series(highestAverage, index=symbols)}
results = pd.DataFrame(results).sort_values('High')
print(results)
name=file.split('.')[0]
results.to_csv(path+name+'_Performance.csv', index=True, header=True)
