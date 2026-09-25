import pandas as pd, time, os
year = time.localtime().tm_year
month = time.localtime().tm_mon

# Make directories for clean prices
for i in ['1y', '3y']:
    os.makedirs(f"prices_cleaned/{i}/{month-1}_{year}", exist_ok = True)

"""
Drop assets with any out-of-range prices
(Range = [Q1 - 1.5IQR, Q3 + 1.5IQR])
"""
def drop_outliers(prices):
    q1 = prices.quantile(0.25)
    q3 = prices.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    has_outlier = (prices.lt(lower) | prices.gt(upper)).any()
    return prices.loc[:, ~has_outlier]

indices = pd.read_excel("Markets_by_Country.xlsx", index_col = 0, header = 0)
looper = list(indices.index)
looper.append('usf')
for i in looper:
    for j in ['1y', '3y']:
       prices = pd.read_csv(f"prices/{j}/{month-1}_{year}/{i}.csv").set_index('Date')
       
       # Drop negative prices
       col = prices.columns[(prices < 0).any()] 
       prices = prices.drop(columns = col)
       
       prices = drop_outliers(prices)
       prices.to_csv(f"prices_cleaned/{j}/{month-1}_{year}/{i}.csv")
       
