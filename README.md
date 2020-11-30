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
	
Results are sorted by Sale Ratio and printed to the screen, as well as saved to a csv file that is created in the same directory as the input file containing the list of symbols.

When the YoungBear metric is less than 1, the share price has been in steady decline in the past short term. When the OldBear metric is less than 1, the share price has been in steady decline for some time. These metrics may also be less than 1 in cases of extremely steep drops. 

The theory behind the usefulness of this script is that the moving average of the share price of a symbol approximates its fair value. Thus, when the Sale, Discount, or Dip ratios are below 1, you may be able to purchase for below fair-value. Of course, the crucial premise here may not be correct; the intrinsic value may be far removed from the average share price over any period of time, and changes to a ticker company's circumstances are not necessarily (or accurately) reflected in share price.


GetFinancialDocs.py
===================
Takes in a file containing a newline-seperated list of ticker symbols and downloads financial documnets using the FMP API. The FMP API requires an API key which can be obtained for free from their website (https://financialmodelingprep.com). This API key must either be passed into the script using the -k flag, or placed in a text document which is passed into the script using the -K flag. The script currently downloads:

	+Balance Sheets (Annual and Quarterly)
	
	+Company profile
	
More financial documents may be supported later. Because 3 documents are downloaded per symbol, this caps the number of symbols you can get docs for per day using the free version of FMP to 83. Documents are saved as json files in the same directory as the list of symbols.


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
