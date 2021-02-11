import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)
import datetime

year = int(input("Year: "))
month = int(input("Month: "))
day = int(input("Day: "))
SP500 = pd.read_csv("SP500Current.csv")
print(SP500)
modifications = pd.read_csv("SP500Modifications.csv", parse_dates=[0])
modifications['Date'] = pd.to_datetime(modifications['Date']).dt.date
m = modifications.loc[modifications['Date'] >= datetime.date(year, month, day)]
for x in range(len(m)):
    if not pd.isna((m['Added'][x])):
        print("Removing: " + (m['Added'][x]))
        SP500.drop(SP500.index[SP500['Symbol'] == m['Added'][x]], inplace = True)    
    if not pd.isna((m['Removed'][x])):
        print("Adding: " + (m['Removed'][x]))
        SP500 = SP500.append({'Symbol': m['Removed'][x]}, ignore_index=True)
print(SP500)
SP500.to_csv('S&P500_'+str(year)+'-'+str(month)+'-'+str(day)+'.csv', index=False)
#SP500.append({'Symbol': 'TRMB'}, ignore_index=True)
#modifications.loc[modifications['Date'] >= datetime.date(2020, 1, 1)]
#SP500.drop(SP500.index[SP500['Symbol'] == ], inplace = True)
