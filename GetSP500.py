import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)
import datetime

year = int(input("Year: "))
month = int(input("Month: "))
day = int(input("Day: "))
SP500 = pd.read_csv("SP500Current.csv")
SP500History = pd.read_csv("SP500ConstituentsActions.csv")
SP500History['Date'] = pd.to_datetime(SP500History['Date']).dt.date
date = SP500History.loc[SP500History['Date'] >= datetime.date(year, month, day)]
for x in range(len(date)):
    if (date['Action'][x] == "added_ticker"):
        print("Removing: " + (date['Ticker'][x]))
        SP500.drop(SP500.index[SP500['Symbol'] == date['Ticker'][x]], inplace = True)    
    if (date['Action'][x] == "removed_ticker"):
        print("Adding: " + (date['Ticker'][x]))
        SP500 = SP500.append({'Symbol': date['Ticker'][x]}, ignore_index=True)
print(SP500)
SP500.to_csv('S&P500_'+str(year)+'-'+str(month)+'-'+str(day)+'.csv', header=False, index=False)
