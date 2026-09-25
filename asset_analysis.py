import pandas as pd, json, time, os
import statsmodels.api as sm, math
year = time.localtime().tm_year
month = time.localtime().tm_mon

# Make directories for returns
for i in ['1y', '3y']:
    os.makedirs(f"returns/{i}/{month-1}_{year}", exist_ok = True)

"""
Read in tickers for reg
"""
def read_tickers(reg):
    with open(f"tickers/{month-1}_{year}/{reg}.json", 'r') as file:
         tickers = json.load(file)
         
    return tickers

"""
Calculate monthly holding period returns
"""
def calc_returns(prices):
    lag = prices.shift(1)
    prices = prices.iloc[1:, :]
    lag = lag.iloc[1:, :]
    returns = (prices - lag)/lag
    returns = returns.replace([np.inf, -np.inf], np.nan)
    returns = returns.dropna(how = "all", axis = 1).dropna(how = "all", axis = 0)
    return returns

"""
Calculate risk, return and Sharpe ratio
"""
def calc_stats(prices):
    return_stats = prices[prices.columns].agg(['mean', 'std']).T
    return_stats['Return'] = ((1 + return_stats['mean'])**12 - 1)*100 # Annualized return
    return_stats['Return'] = return_stats['Return'].round(2)
    return_stats['Risk'] = return_stats['std']*math.sqrt(12) # Annualized risk
    return_stats['Risk'] = return_stats['Risk'].round(3)
    return_stats['sharpe'] = return_stats['mean']/return_stats['std'] # Assuming a risk-free rate of 0% in the market at-large
    return return_stats

"""
Calculate asset volatility, relative to market index
"""
def calc_beta(returns, index, return_stats):
    for i in returns.columns:
       if i != index:
         y = returns[i]
         x = returns[index]
         x = sm.add_constant(x)
         model = sm.OLS(y,x).fit()
         return_stats.loc[i, 'beta'] = model.params.iloc[1]

    return_stats.loc[index, 'beta']  = 1.0
    return_stats['beta_abs'] = return_stats['beta'].abs()
    return_stats['beta_abs'] = return_stats['beta_abs'].round(3)
    return_stats = return_stats.rename(columns = {'beta_abs':'Volatility'})
    return_stats['Follows Market Direction ?'] = pd.cut(return_stats['beta'], bins = [float('-Inf'), 0, float('Inf')], labels = ['No', 'Yes'])
    return return_stats

"""
Sort assets by Sharpe ratio, in descending order
"""
def sort_assets(price_stats):
    return price_stats.sort_values(by = 'sharpe', ascending = False)

"""
Join ticker and name information onto DataFrame for returns
"""
def join_tickers(data, tickers):
    tickers_df = pd.DataFrame.from_dict(tickers, orient = 'index', columns = ['Value'])
    final = data.merge(tickers_df, left_index = True, right_index = True, how = 'left')
    final = final.reset_index()
    final = final.rename(columns = {'Value':'Name', 'index':'Ticker'})
    return final

indices = pd.read_excel("Markets_by_Country.xlsx", index_col = 0, header = 0)
looper = list(indices.index)
looper.append('usf')
for i in looper:
    for j in ['1y', '3y']:
        prices = pd.read_csv(f"prices_cleaned/{j}/{month-1}_{year}/{i}.csv").set_index('Date')
        if len(prices) <= 1 or prices.isna().all().all() == True: # Handling for empty DataFrames
           continue
        r = calc_returns(prices)
        
        if i == 'usf':
           mindex = 'us' # Market index for US-funds
           
        else:
            mindex = i
        
        # If market index figures available
        if(indices.loc[mindex, "Market Index Ticker"] in r.columns):
           final = sort_assets(calc_beta(r, indices.loc[mindex, 'Market Index Ticker'], calc_stats(r)))
        else:
           final = sort_assets(calc_stats(r))
        final = join_tickers(final, read_tickers(i))
        final.to_csv(f"returns/{j}/{month-1}_{year}/{i}.csv", index = False)
       
       
