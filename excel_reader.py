import pandas as pd


def read_file():
    symbol_pd = pd.DataFrame()
    symbol_pd = pd.read_csv('symbols.csv', encoding = "cp1255")
    symbol_weekly = []
    symbol_monthly = []
    for value in symbol_pd.iterrows():
        if value['גרף'] == 'שבועי':
            symbol_weekly.append(value['נייר'])
        if value['גרף'] == 'חודשי':
            symbol_monthly.append(value['נייר'])
    symbol_weekly_pd = pd.DataFrame(symbol_weekly)
    symbol_monthly_pd = pd.DataFrame(symbol_monthly)
    print(symbol_weekly_pd)
    print(symbol_monthly_pd)