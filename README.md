# MarketSims
Projects for gathering market data and simulating trading and investing strategies

SymbolPerformance.py
====================
Takes in a file containing a newline-seperated list of ticker symbols and reports the stock price performance for each of them using the Yahoo Finance API (no API key required). The script reports:

	+Sale Ratio: The price-to-15 day Moving Average ratio.
	
	+Discount:   The price-to-30 day Moving Average ratio.
	
	+Dip:        The price-to-180 day Moving Average ratio.
	
	+YoungBear:  The 15 day to 30 day Moving Average ratio.
	
	+OldBear:	The 15 day to 180 day Moving Average ratio.
	
	+High:		The price to 52-week high (actually, 30-day moving average 15 days after 52-week high, to account for sudden spikes)
	
Results are sorted using the High metric and printed to the screen, as well as saved to a csv file that is created in the same directory as the input file containing the list of symbols.

When the YoungBear metric is less than 1, the share price has been in steady decline in the past short term. When the OldBear metric is less than 1, the share price has been in steady decline for some time. These metrics may also be less than 1 in cases of extremely steep drops. 

The theory behind the usefulness of this script is that the moving average of the share price of a symbol approximates its fair value. Thus, when the Sale, Discount, or Dip ratios are below 1, you may be able to purchase for below fair-value. Of course, the crucial premise here may not be correct; the intrinsic value may be far removed from the average share price over any period of time, and changes to a ticker company's circumstances are not necessarily (or accurately) reflected in share price.


GetFinancialDocs.py
===================
Takes in a file containing a newline-seperated list of ticker symbols and downloads financial documnets using the FMP API. The FMP API requires an API key which can be obtained for free from their website (https://financialmodelingprep.com). This API key must either be passed into the script using the -k flag, or placed in a text document which is passed into the script using the -K flag. The script currently downloads:

	+Balance Sheets (Annual and Quarterly)
	
	+Company profile
	
	+Key Metrics
	
	+Income Statements (Annual and Quarterly)
	
More financial documents may be supported later. Because 7 documents are downloaded per symbol, this caps the number of symbols you can get docs for per day using the free version of FMP to 35. Documents are saved as json files in the same directory as the list of symbols.


CreateEvaluations.py
====================
Takes in a file containing a newline-seperated list of ticker symbols and uses financial documents to evaluate each companies debt management. More metrics may be added in future editions. JSON versions of annual and quarterly balance sheets and company profiles must be present in the same directory as the list of ticker symbols and can be obtained using GetFinancialDocs.py.

The script runs a linear regression on annual receivables, net property plant and equipment, and Long Term Debt to see what the company's trend in these regards is. We like to see a decline in LTD, but even if LTD is non-decreasing, it should at least not be growing faster than receivables or property; a company taking out debt just to survive or grow slowly is not managing their debt well, and we may not want to consider investing.

The script also reports Short term debt over cash and LTD over Receivables using the average of the past 2 quarters to represent current status. The idea here is that even if LTD is decreasing, massive amounts of debt that cannot be paid in a reasonable time are unattractive. Of course, some industries (like REITs) may be expected to have large amounts of debt relative to their net receivables. For this, future editions of the script may also report price-to-book value ratios.
The script reports:

	+STD/Cash: Short Term Debt over Cash
	
	+LTDoverREC: Long Term Debt of Receivables
	
	+dividend: Dividend yield
	
	+rec mean/m: Average receivables over the slope of the least squares estimate for receivables. Positive numbers close to 0 are desirable.
	
	+ppe mean/m: Average net PPE over the slop of the least squares estimate for PPE. Positive numbers close to 0 are desirable.
	
	+ltd mean/m: Average long term debt over the slope of the least squares estimate for LTD. Negative numbers close to 0 are desirable. 
	

Because the rec, ppe, and ltd mean/m metrics can be confusing, it is possible to create rec, ppe, and ltd SCORE metrics. For rec and ppe, divide 100 by the mean/m value. For ltd, divide -100 by the mean/m value. This gives us scores that can be sorted, with higher scores being more desirable than lower scores, and score values generally appearing between -100 and 100.

This script has need for improvements, both in quality of the code and scope of function. For now, it is useful for tracking metrics that I value most in evaluating a company's worthiness for investment.

The option for doing historic analysis has been added, but there are a variety of issues. The goal is to perform the evaluation on data as if the analysis were being done at some point in the past, then compare the results to actual performance. This way, it can be seen if there is any real correlations between my evaluations and stock performance. Issues abound both in concept and in practice:
	1) Survivorship bias. Performing historical analysis on the companies that are currently in the S&P500 is useless, since these companies have performed well regardless of their status 10 years ago.
	2) Available data. I recently discover that BIIB was getting a good historical evaluation because the EPS data was taken from the late 90's while debt and ticker price were from the early 90's. I need to clean up the data OR (preferably) re-write the script to use dates rather than list indexes.

GetSP500.py
====================
Accepts user input for a date in the past, then finds what the S&P500 components on that date were. This script is poorly designed and still in its infancy, but I needed a quick-fix for getting old S&P500 tickers. These will be useful for avoiding survivorship bias in evaluations; companies currently in the S&P500 will obviously have performed well regardless of their historic analysis (using --historic flag of CreateEvaluations.py) -- that is why they are in the index. What we really want is to do a historic analysis on the tickers that used to be in the index.
Constituent data was gathered and combined from Wikipedia and https://github.com/leosmigel/analyzingalpha/blob/master/sp500-historical-components-and-changes/sp500_history.csv. 
