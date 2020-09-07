import yfinance as yf
import matplotlib.pyplot as plt
import seaborn
import pandas as pd

#symbols = ["BA", "LUV", "NFLX", "AMD", "LMT", "SPOT", "CBRL", "SAFM", "HAS", "INTC", "ATVI", "AMZN", "CSCO"]
symbols = [line.rstrip('\n') for line in open("Dow30.txt")]
data_df = yf.download(tickers=symbols, period='1y', interval='1d', rounding='True')
data_df = data_df['Close']
size = len(data_df)
#The following maps averages to the list of symbols
fifteenDayAVG = []
thirtyDayAVG = []
sixMonthAVG = []
priceTo15dma = [] #less than 1 means the share price is lower than its 15-day mean
priceTo30dma = [] #less than 1 means the share price is lower than its 30-day mean
shortTermBear = [] #True if the 15-day mean is under the 30-day mean
longTermBear = [] #True if the 15-day mean is under the 6-month mean

for sym in symbols:
    fifteenDayAVG.append(data_df[size-15:][sym].mean())
    thirtyDayAVG.append(data_df[size-30:][sym].mean())
    sixMonthAVG.append(data_df[size-180:][sym].mean())
    sharePrice = data_df[sym][size-1]
    priceTo15dma.append(sharePrice / fifteenDayAVG[-1])
    priceTo30dma.append(sharePrice / thirtyDayAVG[-1])
    shortTermBear.append(fifteenDayAVG[-1] < thirtyDayAVG[-1])
    longTermBear.append(fifteenDayAVG[-1] < sixMonthAVG[-1])
    
#Create dataframe from the information calculated above    
results = {'Sale ratio': pd.Series(priceTo15dma, index=symbols),
           'Discount': pd.Series(priceTo30dma, index=symbols),
	   'ShortBear': pd.Series(shortTermBear, index=symbols),
	   'LongBear': pd.Series(longTermBear, index=symbols)}
results = pd.DataFrame(results).sort_values('Sale ratio')
print(results)

