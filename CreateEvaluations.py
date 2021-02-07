import json
import pandas as pd
import numpy as np
import statistics as stats
import os
import sys, getopt
import yfinance as yf
pd.set_option("display.max_rows", None, "display.max_columns", None)
path = os.path.dirname(os.path.realpath(__file__))+'/'
file=''

#Read CL arguments
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], 'hi:p:o:H')
except getopt.GetoptError as err:
    print(str(err))
    print('SymbolPerformance.py -h for usage')
    sys.exit(2)
for opt, arg in opts:
    if opt in("-h", "--help"):
        print(' -i <input file> \t Filename of file that contains list of symbols seperated by newlines. Must be in same directory as this script, unless the -p flag is used.')
        print(' -p, --path=<directory> \t Directory for this script to work in. Working directory by default.')
        print(' -o <outfile> \t Filename of a file that will be written to rather than stdout. This only affects what is normally printed to the terminal.')
        print(' -H, --historic \t Perform analysis using oldest data available, as if you were using this script in the past. Helpful for determining efficacy of this script. BEWARE SURVIVORSHIP BIAS!')
        sys.exit(2)
    elif opt in ('-i', "--infile"):
        file = arg
    elif opt in ('-p', "--path"):
        path = arg+'/'
    elif opt in ('-o'):
        outfile = path+arg
        sys.stdout = open(outfile, 'w')
    elif opt in ('-H', "--historic"):
        historicAnalysis = True
        historicString = '_Historic'
if (file==''):
    print('Must have input file. See SymbolPerformance.py -h for usage')
    sys.exit(2)
    
#Globals
symbols = [line.rstrip('\n') for line in open(path+file)]
symbol_analysis = {}
skipped = []
maxInt = 2**63 - 1
sciNot='{:.2E}' #Scientific Notation
historicString='_'
historicAnalysis=False

#Record and display error when missing crucial data points
badMessages = []
def badDataMessage(data, symbol):
    messageStr = ("***INSUFFICIENT "+data+" DATA FOR ANALYSIS of "+symbol+" ***\n")
    print(messageStr)
    badMessages.append(messageStr)
    
print("We will take a list of symbols and evaluate the company using their financial documentation.\n")
print("Important numbers:")
print("\tm: the slope of the least squares linear regression")
print("\tmean/m: Essentially, how many years until the mean is reached from the growth rate. Negative means it will be reduced to 0, positive means it will be doubled.")
print("\t        For LTD, we want a negative number close to 0 or a positve number much greater than 0. For Net Receivables, the opposite.")

for symbol in symbols:
    #Load data and create relevant variables
    with open(path+symbol+'profile.json', 'r') as read_file:
        profile = json.load(read_file)
        try:
            price = profile[0]['price']
        except (IndexError, KeyError):
            skipped.append(symbol)
            badDataMessage("Profile", symbol)
            continue
        if (price == 0):
            skipped.append(symbol)
            badDataMessage("Price", symbol)
            continue
        description = profile[0]['description'] if ('description' in profile[0]) else "[n/a]"
        dividend = profile[0]['lastDiv']/price*100 if ('lastDiv' in profile[0]) else 0
    with open(path+symbol+'quarterlyKeyMetrics.json', 'r') as read_file:
        quarterlyData = json.load(read_file) #quarterlyData[0] is most recent
        if (historicAnalysis):
            quarterlyData = quarterlyData[-10:] #If doing historic analysis, use first 10 years available
        numQuarters = min(len(quarterlyData), 10) #Use at most last 10 quarters of data
        quarterly = {}
        RANGE = range(numQuarters-1,-1,-1) #We want our list to end in the present, but quarterlyData[0] is most recent.
        metrics = ['bookValuePerShare', 'netIncomePerShare']
        for metric in metrics:
            quarterly[metric] = [quarterlyData[n][metric] for n in RANGE]
        try:
            bvPerShare = stats.mean(quarterly['bookValuePerShare'][-4:])
        except:
            badDataMessage("quarterly BV/share", symbol)
            bvPerShare = 0
            #THIS NEEDS DRAMATIC IMPROVEMENT BUT IT IS ALMOST BEDTIME
        try:
            quarterlyEPS = stats.mean(quarterly['netIncomePerShare'][-4:])
        except:
            badDataMessage("quarterly EPS", symbol)
            quarterlyEPS = 0
            #THIS NEEDS DRAMATIC IMPROVEMENT BUT IT IS ALMOST BEDTIME
    with open(path+symbol+'annualKeyMetrics.json', 'r') as read_file:
        annualData = json.load(read_file)
        if (historicAnalysis):
            annualData = annualData[-10:]
        numYears = min(10, len(annualData)) #User at most last 10 years of data
        RANGE = range(numYears-1,-1,-1)
        annual = {}
        for metrics in metrics:
            annual[metric] = [annualData[n][metric] for n in RANGE]
        try:
            annualEPS = stats.mean(annual['netIncomePerShare'][-3:])
        except:
            badDataMessage("annual EPS", symbol)
            annualEPS = 0
            #THIS NEEDS DRAMATIC IMPROVEMENT BUT IT IS ALMOST BEDTIME
    #Source quarterly Balance Sheet Data
    with open(path+symbol+'quarterlyBalanceSheet.json', 'r') as read_file:
        quarterlyData = json.load(read_file)
        if (historicAnalysis):
            quarterlyData = quarterlyData[-10:]
        numQuarters = min(10, len(quarterlyData))
        RANGE = range(numQuarters-1,-1,-1)
        quarterly = {}
        metrics = ['date', 'cashAndCashEquivalents', 'shortTermDebt', 'netReceivables', 'longTermDebt']
        for metric in metrics:
            quarterly[metric] = [quarterlyData[n][metric] for n in RANGE]
        quarterly_df = pd.DataFrame([quarterly['cashAndCashEquivalents'], quarterly['shortTermDebt'], quarterly['longTermDebt']])
        quarterly_df.columns=quarterly['date']
        quarterly_df.index=['cash', 'shortTermDebt', 'longTermDebt']
        try:
            STDoverCASH = stats.mean(quarterly['shortTermDebt'][-2:])/stats.mean(quarterly['cashAndCashEquivalents'][-2:])
        except ZeroDivisionError:
            STDoverCASH = maxInt
        except stats.StatisticsError:
            badDataMessage("Quarterly STD", symbol)
            skipped.append(symbol)
            continue
        try:
            LTDoverREC = stats.mean(quarterly['longTermDebt'][-2:])/stats.mean(quarterly['netReceivables'][-2:])
        except ZeroDivisionError:
            LTDoverREC = maxInt
        except stats.StatisticsError:
            badDataMessage("Quarterly LTD", symbol)
            skipped.append(symbol)
            continue
    #Source annual Balance Sheet Data
    with open(path+symbol+'annualBalanceSheet.json', 'r') as read_file:
        annualData = json.load(read_file)
        if (historicAnalysis):
            annualData = annualData[-10:]
        numYears = min(10, len(annualData))
        RANGE = range(numYears-1,-1,-1)
        annual = {}
        metrics = ['date', 'cashAndCashEquivalents', 'netReceivables', 'propertyPlantEquipmentNet', 'shortTermDebt', 'longTermDebt']
        for metric in metrics:
            annual[metric] = [annualData[n][metric] for n in RANGE]
        annualMetrics = [annual['cashAndCashEquivalents'], annual['shortTermDebt'],annual['netReceivables'],
                   annual['propertyPlantEquipmentNet'], annual['longTermDebt']]
        annual_df = pd.DataFrame(annualMetrics,
                                 columns=annual['date'],
                                 index=['cash', 'shortTermDebt','netReceivables',
                                        'PPE', 'longTermDebt'])
    #Begin Analysis
    analysis=[STDoverCASH, LTDoverREC, dividend, bvPerShare, annualEPS, quarterlyEPS]
    analysis = [round(n, 4) for n in analysis]
    #DisplayData
    print(description[:60])
    print(quarterly_df)
    print('\n')
    print(annual_df)
    print('\n')
    #Least squares for annual Longterm Debt, receivables, and NPPE.
    if (numYears > 1): #Cannot do linear regression without at least 2 data points
        a = [n for n in range(min(5, numYears))]
        a_length = len(a)
        A = np.vstack([a, np.ones(a_length)]).T
        slope = {}
        intercept = {}
        metrics = ['netReceivables', 'propertyPlantEquipmentNet', 'longTermDebt']
        for metric in metrics:
            slope[metric], intercept[metric] = np.linalg.lstsq(A, annual[metric][-a_length:], rcond=None)[0]
        annualMeans = {}
        annualVars = {}
        for metric in metrics:
            annualMeans[metric] = stats.mean(annual[metric][-a_length:])
            annualVars[metric] = stats.variance(annual[metric][-a_length:])
        annualResults = {}
        for metric in metrics:
            annualResults[metric] = [slope[metric], intercept[metric], annualMeans[metric], annualMeans[metric]/slope[metric], annualVars[metric]**0.5]
        print("\t\tm \t c \t mean \t mean/m \t mean/StdDev")
        for metric in metrics:
            print(metric + ": ", list(map(sciNot.format, annualResults[metric])))
        print('\n')
        for metric in metrics:
            try:
                #Mean/variance gives an idea of how suddenly large changes are occurring
                #Ex, taking out debt gradually or a lot suddenly
                analysis.append(round(annualResults[metric][2]/annualResults[metric][4], 4))
            except ZeroDivisionError:
                analysis.append('nan')
            analysis.append(round(annualResults[metric][3], 4))
    else:
        badDataMessage("Annual", symbol)
        skipped.append(symbol)
        continue
    analysis.append(round((2/3)*bvPerShare, 4))
    analysis.append(round((2/3)*bvPerShare + 10*annualEPS, 4))
    analysis.append(round((2/3)*bvPerShare + 20*annualEPS, 4))
    annualLTDgrowth = annualResults['longTermDebt'][3]
    annualPPEgrowth = annualResults['propertyPlantEquipmentNet'][3]
    annualRECgrowth = annualResults['netReceivables'][3]
    rating = 0
    if (STDoverCASH < 4):
        rating +=1
    if (LTDoverREC < 7):
        rating +=2
    if (dividend > 2.5):
        rating +=0.5
    if (annualLTDgrowth < 0 and annualLTDgrowth > -10): 
        rating +=1
        if (annualLTDgrowth > -5 and LTDoverREC > 5): #Paying off debt fast is easy when you don't have much
            rating +=1
    if (annualLTDgrowth >= 0):
        if ((annualLTDgrowth > annualRECgrowth) and (annualRECgrowth > 0)):
            rating+=0.5
        if ((annualLTDgrowth > annualPPEgrowth) and (annualPPEgrowth > 0)):
            rating+=0.5
    if (annualLTDgrowth > 0 and annualLTDgrowth < 5):
        rating -=1
    if (annualRECgrowth > 0 and annualRECgrowth <5):
        rating +=2   
    analysis.append(rating)
    if (historicAnalysis):      
        data_df = yf.download(tickers=symbol, start=annualData[0]['date'], rounding='True', actions=True)
        twelvemonthLow = min(data_df['Close'][:300]) #What was the cheapest you could buy the security around this time?
        tenyrlater = data_df['Close'][min(3000, len(data_df)-1)] #What was the security's price 10yrs later (or last available quote)
        analysis.append(twelvemonthLow)
        analysis.append(tenyrlater)
        analysis.append(price)
        analysis.append(annualData[0]['date'])
    else:
        analysis.append(price)
    symbol_analysis[symbol] = analysis

for message in badMessages:
    print(message)
print("Skipped: ",skipped)
tablecolumns = ["STD/Cash", "LTDoverREC", "dividend",
                "BV/share", "annualEPS", "quarterlyEPS",
                "rec mean/stdDev", "rec mean/m",
                "ppe mean/stdDev", "ppe mean/m",
                "ltd mean/stdDev", "ltd mean/m",
                "Estimate1", "Estimate2", "Estimate3",
                "Rating", "Price"]
if (historicAnalysis):
    tablecolumns += ["10yrlatr", "Today", "LastDate"]
results = pd.DataFrame.from_dict(symbol_analysis, orient='index', columns=tablecolumns)
print(results)
name=file.split('.')[0]
results.to_csv(path+name+historicString+'Analysis.csv', index=True, header=True)
#sys.stdout.close()
