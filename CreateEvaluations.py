import json
import pandas as pd
import numpy as np
import statistics as stats
import os
import sys, getopt
pd.set_option("display.max_rows", None, "display.max_columns", None)
path = os.path.dirname(os.path.realpath(__file__))+'/'
file=''
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
symbols = [line.rstrip('\n') for line in open(path+file)]
symbol_analysis = {}
skipped = []

print("We will take a list of symbols and evaluate the company using their financial documentation.\n")
print("Important numbers:")
print("\tm: the slope of the least squares linear regression")
print("\tmean/m: Essentially, how many years until the mean is reached from the growth rate. Negative means it will be reduced to 0, positive means it will be doubled. For LTD, we want a negative number close to 0 or a positve number much greater than 0. For Net Receivables, the opposite.")

for symbol in symbols:
    #Load data and create relevant variables
    with open(path+symbol+'profile.json', 'r') as read_file:
        profile = json.load(read_file)
        try:
            price = profile[0]['price']
        except (IndexError, KeyError):
            skipped.append(symbol)
            print("***INSUFFICIENT PROFILE DATA FOR MANAGEMENT ANALYSIS of "+symbol+" ***\n")
            continue
        if (price == 0):
            skipped.append(symbol)
            continue
        description = profile[0]['description']
        mktCap = profile[0]['mktCap']
        beta = profile[0]['beta']
        dividend = profile[0]['lastDiv']/price*100
    with open(path+symbol+'ttmRatios.json', 'r') as read_file:
        ratios = json.load(read_file)
        try: #Only need to try 1 to see if json was empty
            priceToBV = ratios[0]['priceToBookRatioTTM']
        except (IndexError, KeyError):
            skipped.append(symbol)
            print("***INSUFFICIENT TTMRATIOS DATA FOR MANAGEMENT ANALYSIS of "+symbol+" ***\n")
            continue
        priceToBV = 0 if priceToBV is None else priceToBV
        priceToSales = ratios[0]['priceToSalesRatioTTM']
        priceToSales = 0 if priceToSales is None else priceToSales
        priceToEarnings = ratios[0]['priceEarningsRatioTTM']
        priceToEarnings = 0 if priceToEarnings is None else priceToEarnings
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
            STDoverCASH = 2**63 - 1
        except stats.StatisticsError:
            print("***INSUFFICIENT QUARTERLY DATA FOR MANAGEMENT ANALYSIS of "+symbol+" ***\n")
            skipped.append(symbol)
            continue
        try:
            LTDoverREC = stats.mean(quarterly_longTermDebt[-2:])/stats.mean(quarterly_netReceivables[-2:])
        except ZeroDivisionError:
            LTDoverREC = 2**63 - 1
        except stats.StatisticsError:
            print("***INSUFFICIENT QUARTERLY DATA FOR MANAGEMENT ANALYSIS of "+symbol+" ***\n")
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
    analysis=[STDoverCASH, LTDoverREC, dividend, priceToBV, priceToSales, priceToEarnings]
    analysis = [round(n, 4) for n in analysis]
    #DisplayData
    print(description[:40], mktCap, beta)
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
        sciNot='{:.2E}' #Scientific Notation
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
        print("***INSUFFICIENT ANNUAL DATA FOR MANAGEMENT ANALYSIS of "+symbol+" ***\n")
    symbol_analysis[symbol] = analysis

print("Skipped: ",skipped)
tablecolumns = ["STD/Cash", "LTDoverREC", "dividend",
                "price/BV", "p/Sales", "p/e",
                "rec mean", "rec mean/m", "rec stdDev",
                "ppe mean", "ppe mean/m","ppe stdDev",
                "ltd mean", "ltd mean/m","ltd stdDev"]
results = pd.DataFrame.from_dict(symbol_analysis, orient='index', columns=tablecolumns)
print(results)
name=file.split('.')[0]
results.to_csv(path+name+'_Analysis.csv', index=True, header=True)
sys.stdout.close()
