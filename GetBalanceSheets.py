#!/usr/bin/env python
symbols = [line.rstrip('\n') for line in open("Dow30.txt")]
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

for symbol in symbols:
    annual = ("https://financialmodelingprep.com/api/v3/balance-sheet-statement/"+symbol+"?limit=120&apikey=cb7330bc0a6b4dc2a7446f2bc5b0a358")
    quarterly = ("https://financialmodelingprep.com/api/v3/balance-sheet-statement/"+symbol+"?period=quarter&limit=6&apikey=cb7330bc0a6b4dc2a7446f2bc5b0a358")
    #print(get_jsonparsed_data(url))
    annual_json = get_jsonparsed_data(annual)
    quarterly_json = get_jsonparsed_data(quarterly)
    with open(symbol+'annualBalanceSheet.json', 'w') as outfile:
        json.dump(annual_json, outfile)
    with open(symbol+'quarterlyBalanceSheet.json', 'w') as outfile:
        json.dump(quarterly_json, outfile)
    
