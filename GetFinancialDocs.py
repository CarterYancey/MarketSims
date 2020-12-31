#!/usr/bin/env python
import os
import sys, getopt
import json

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def main(argv):
    global path
    path = os.path.dirname(os.path.realpath(__file__))+'/'
    global infile
    infile=''
    global apikey
    apikey=''
    try:
        opts, args = getopt.gnu_getopt(argv, 'hi:k:K:p:')
    except getopt.GetoptError as err:
        print(str(err))
        print('GetFinancialDocs.py -h for usage')
        sys.exit(2)
    for opt, arg in opts:
        if opt in("-h", "--help"):
            print(' -i <input file> \t Filename of file that contains list of symbols seperated by newlines. Must be in same directory as this script, unless the -p flag is used.')
            print(' -k <api key> \t API key for FMP.')
            print(' -K <input file> \t Filename of file that contains API key.')
            print(' -p, --path=<directory> \t Directory for this script to work in. Working directory by default.')
            sys.exit(2)
        elif opt in ('-i', "--infile"):
            infile = arg
        elif opt in ('-k', "--key"):
            apikey = arg
        elif opt in ('-K'):
            apikey = open(path+arg, 'r').read()
        elif opt in ('-p', "--path"):
            path = arg+'/'
    if (infile=='' or apikey==''):
        print('Must have input file and API key. See GetFinancialDocs.py -h for usage')
        sys.exit(2)   
    symbols = [line.rstrip('\n') for line in open(path+infile)]
    for symbol in symbols:
        get_balanceSheet(symbol)
        get_profile(symbol)
        get_keyMetrics(symbol)

def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    data_json = json.loads(data)
    return data_json

def get_balanceSheet(symbol):
    annual = ("https://financialmodelingprep.com/api/v3/balance-sheet-statement/"+symbol+"?limit=120&apikey="+apikey)
    quarterly = ("https://financialmodelingprep.com/api/v3/balance-sheet-statement/"+symbol+"?period=quarter&limit=6&apikey="+apikey)
    annual_json = get_jsonparsed_data(annual)
    quarterly_json = get_jsonparsed_data(quarterly)
    with open(path+symbol+'annualBalanceSheet.json', 'w') as outfile:
        json.dump(annual_json, outfile)
    with open(path+symbol+'quarterlyBalanceSheet.json', 'w') as outfile:
        json.dump(quarterly_json, outfile)
    
def get_profile(symbol):
    profile = ("https://financialmodelingprep.com/api/v3/profile/"+symbol+"?limit=120&apikey="+apikey)
    profile_json = get_jsonparsed_data(profile)
    with open(path+symbol+'profile.json', 'w') as outfile:
        json.dump(profile_json, outfile)

def get_keyMetrics(symbol):
    metrics = ("https://financialmodelingprep.com/api/v3/key-metrics/"+symbol+"?period=quarter&limit=130&apikey="+apikey)
    metrics_json = get_jsonparsed_data(metrics)
    with open(path+symbol+'keyMetrics.json', 'w') as outfile:
        json.dump(metrics_json, outfile)

if __name__ == "__main__":
   main(sys.argv[1:])
