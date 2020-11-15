#!/usr/bin/env python
symbols = [line.rstrip('\n') for line in open("C:/Users/carte/MarketSims/SP500/SP1to125.txt")]
apikey=""
#directory=""

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import json

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
    with open(symbol+'annualBalanceSheet.json', 'w') as outfile:
        json.dump(annual_json, outfile)
    with open(symbol+'quarterlyBalanceSheet.json', 'w') as outfile:
        json.dump(quarterly_json, outfile)
    
def get_profile(symbol):
    profile = ("https://financialmodelingprep.com/api/v3/profile/"+symbol+"?limit=120&apikey="+apikey)
    profile_json = get_jsonparsed_data(profile)
    with open(symbol+'profile.json', 'w') as outfile:
        json.dump(profile_json, outfile)

for symbol in symbols:
    get_balanceSheet(symbol)
    get_profile(symbol)
