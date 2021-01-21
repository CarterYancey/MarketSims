import json
import pandas as pd
import numpy as np
import statistics as stats
import os
import sys, getopt
pd.set_option("display.max_rows", None, "display.max_columns", None)
path = os.path.dirname(os.path.realpath(__file__))+'/'
file=''

#Read CL arguments
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], 'hi:p:o:')
except getopt.GetoptError as err:
    print(str(err))
    print('SymbolPerformance.py -h for usage')
    sys.exit(2)
for opt, arg in opts:
    if opt in("-h", "--help"):
        print(' -i <input file> \t Filename of file that contains list of symbols seperated by newlines. Must be in same directory as this script, unless the -p flag is used.')
        print(' -p, --path=<directory> \t Directory for this script to work in. Working directory by default.')
        print(' -o <outfile> \t Filename of a file that will be written to rather than stdout. This only affects what is normally printed to the terminal.')
        sys.exit(2)
    elif opt in ('-i', "--infile"):
        file = arg
    elif opt in ('-p', "--path"):
        path = arg+'/'
    elif opt in ('-o'):
        outfile = path+arg
        sys.stdout = open(outfile, 'w')
if (file==''):
    print('Must have input file. See SymbolPerformance.py -h for usage')
    sys.exit(2)
    
#Globals
symbols = [line.rstrip('\n') for line in open(path+file)]
symbol_analysis = {}
skipped = []
maxInt = 2**63 - 1
sciNot='{:.2E}' #Scientific Notation

def badDataMessage(data, symbol):
    print("***INSUFFICIENT "+data+" DATA FOR MANAGEMENT ANALYSIS of "+symbol+" ***\n")
    
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
            continue
        description = profile[0]['description'] if ('description' in profile[0]) else "[n/a]"
        dividend = profile[0]['lastDiv']/price*100 if ('lastDiv' in profile[0]) else 0
    with open(path+symbol+'quarterlyKeyMetrics.json', 'r') as read_file:
        quarterly = json.load(read_file)
        quarters = len(quarterly)
        quarterly_bookValuePerShare = [quarterly[n]['bookValuePerShare'] for n in range(quarters-1,-1,-1)]
        quarterly_netIncomePerShare = [quarterly[n]['netIncomePerShare'] for n in range(quarters-1,-1,-1)]
        try:
            bvPerShare = stats.mean(quarterly_bookValuePerShare[-4:])
        except:
            badDataMessage("quarterly BV/share", symbol)
            bvPerShare = 0
            #THIS NEEDS DRAMATIC IMPROVEMENT BUT IT IS ALMOST BEDTIME
        try:
            quarterlyEPS = stats.mean(quarterly_netIncomePerShare[-4:])
        except:
            badDataMessage("quarterly EPS", symbol)
            quarterlyEPS = 0
            #THIS NEEDS DRAMATIC IMPROVEMENT BUT IT IS ALMOST BEDTIME
    with open(path+symbol+'annualKeyMetrics.json', 'r') as read_file:
        annual = json.load(read_file)
        years = len(annual)
        annual_bookValuePerShare = [annual[n]['bookValuePerShare'] for n in range(years-1,-1,-1)]
        annual_netIncomePerShare = [annual[n]['netIncomePerShare'] for n in range(years-1,-1,-1)]
        try:
            annualEPS = stats.mean(annual_netIncomePerShare[-3:])
        except:
            badDataMessage("annual EPS", symbol)
            annualEPS = 0
            #THIS NEEDS DRAMATIC IMPROVEMENT BUT IT IS ALMOST BEDTIME
    with open(path+symbol+'quarterlyBalanceSheet.json', 'r') as read_file:
        quarterly = json.load(read_file)
        quarters = len(quarterly)
        quarterly_dates = [quarterly[n]['date'] for n in range(quarters-1,-1,-1)]
        quarterly_cash = [quarterly[n]['cashAndCashEquivalents'] for n in range(quarters-1,-1,-1)]
        quarterly_shortTermDebt = [quarterly[n]['shortTermDebt'] for n in range(quarters-1,-1,-1)]
        quarterly_netReceivables = [quarterly[n]['netReceivables'] for n in range(quarters-1,-1,-1)]
        quarterly_longTermDebt = [quarterly[n]['longTermDebt'] for n in range(quarters-1,-1,-1)]
        quarterly_df = pd.DataFrame([quarterly_cash, quarterly_shortTermDebt, quarterly_longTermDebt])
        quarterly_df.columns=quarterly_dates
        quarterly_df.index=['cash', 'shortTermDebt', 'longTermDebt']
        try:
            STDoverCASH = stats.mean(quarterly_shortTermDebt[-2:])/stats.mean(quarterly_cash[-2:])
        except ZeroDivisionError:
            STDoverCASH = maxInt
        except stats.StatisticsError:
            badDataMessage("Quarterly STD", symbol)
            skipped.append(symbol)
            continue
        try:
            LTDoverREC = stats.mean(quarterly_longTermDebt[-2:])/stats.mean(quarterly_netReceivables[-2:])
        except ZeroDivisionError:
            LTDoverREC = maxInt
        except stats.StatisticsError:
            badDataMessage("Quarterly LTD", symbol)
            skipped.append(symbol)
            continue
    with open(path+symbol+'annualBalanceSheet.json', 'r') as read_file:
        annual = json.load(read_file)
        years = len(annual)
        #I should make these all dictionary entries
        annual_dates = [annual[n]['date'] for n in range(years-1,-1,-1)]
        annual_cash = [annual[n]['cashAndCashEquivalents'] for n in range(years-1,-1,-1)]
        annual_netReceivables = [annual[n]['netReceivables'] for n in range(years-1,-1,-1)]
        annual_PPE = [annual[n]['propertyPlantEquipmentNet'] for n in range(years-1,-1,-1)]
        annual_shortTermDebt = [annual[n]['shortTermDebt'] for n in range(years-1,-1,-1)]
        annual_longTermDebt = [annual[n]['longTermDebt'] for n in range(years-1,-1,-1)]
        annuals = [annual_cash, annual_shortTermDebt,annual_netReceivables,
                   annual_PPE, annual_longTermDebt]
        annual_df = pd.DataFrame(annuals,
                                 columns=annual_dates,
                                 index=['cash', 'shortTermDebt','netReceivables',
                                        'PPE', 'longTermDebt'])
    analysis=[STDoverCASH, LTDoverREC, dividend, bvPerShare, annualEPS, quarterlyEPS]
    analysis = [round(n, 4) for n in analysis]
    #DisplayData
    print(description[:60])
    print(quarterly_df)
    print('\n')
    print(annual_df)
    print('\n')
    #Least squares for annual Longterm Debt, receivables, and NPPE.
    if (years > 1): #Cannot do linear regression without at least 2 data points
        a = [n for n in range(years)]
        A = np.vstack([a, np.ones(len(a))]).T
        m_rec, c_rec = np.linalg.lstsq(A, annual_netReceivables, rcond=None)[0]
        m_ppe, c_ppe = np.linalg.lstsq(A, annual_PPE, rcond=None)[0]
        m_ltd, c_ltd = np.linalg.lstsq(A, annual_longTermDebt, rcond=None)[0]
        annualRECMean = stats.mean(annual_netReceivables)
        annualPPEMean = stats.mean(annual_PPE)
        annualLTDMean = stats.mean(annual_longTermDebt)
        annualRECVar = stats.variance(annual_netReceivables)
        annualPPEVar = stats.variance(annual_PPE)
        annualLTDVar = stats.variance(annual_longTermDebt)
        results_rec = [m_rec, c_rec, annualRECMean, annualRECMean/m_rec, annualRECVar**0.5]
        results_ppe = [m_ppe, c_ppe, annualPPEMean, annualPPEMean/m_ppe, annualPPEVar**0.5]
        results_ltd = [m_ltd, c_ltd, annualLTDMean, annualLTDMean/m_ltd, annualLTDVar**0.5]
        print("\t\tm \t c \t mean \t mean/m \t mean/StdDev")
        print("rec: ", list(map(sciNot.format, results_rec)))
        print("ppe: ", list(map(sciNot.format, results_ppe)))
        print("ltd: ", list(map(sciNot.format, results_ltd)))
        print('\n')
        for result in results_rec[2:]:
            analysis.append(round(result, 4))
        for result in results_ppe[2:]:
            analysis.append(round(result, 4))
        for result in results_ltd[2:]:
            analysis.append(round(result, 4))
    else:
        badDataMessage("Annual", symbol)
    symbol_analysis[symbol] = analysis

print("Skipped: ",skipped)
tablecolumns = ["STD/Cash", "LTDoverREC", "dividend",
                "BV/share", "annualEPS", "quarterlyEPS",
                "rec mean", "rec mean/m", "rec stdDev",
                "ppe mean", "ppe mean/m","ppe stdDev",
                "ltd mean", "ltd mean/m","ltd stdDev"]
results = pd.DataFrame.from_dict(symbol_analysis, orient='index', columns=tablecolumns)
print(results)
name=file.split('.')[0]
results.to_csv(path+name+'_Analysis.csv', index=True, header=True)
sys.stdout.close()
