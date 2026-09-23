import pandas as pd, yfinance as yf, time, json, os, glob
year = time.localtime().tm_year
month = time.localtime().tm_mon

# Make directories to store prices
for i in ['1y', '3y']:
    os.makedirs(f"prices/{i}/{month-1}_{year}", exist_ok = True)

"""
Read in tickers for reg
"""
def read_tickers(reg):
    with open(f"tickers/{month-1}_{year}/{reg}.json", 'r') as file:
         tickers = json.load(file)
         
    return tickers

"""
Pull 3y-prices for tickers and filter for end-of-month prices only
"""
def pull_prices(tickers):
    data = yf.download(tickers, period = '3y')['Close'].reset_index()
    data['Month'] = data['Date'].dt.month
    data['Lead_Month'] = data['Month'].shift(-1)
    data = data[data['Month'] != data['Lead_Month']]
    data = data.drop(['Month', 'Lead_Month'], axis = 1).set_index('Date')
    return data

"""
Slice out prices for the most recent mnths months
"""
def cut_prices(data, mnths):
    return data.iloc[-mnths:,]

"""
Clear cache files for i
"""
def remove_cache(i):
    for f in glob.glob(f"cache/{i}*.pkl"):
        os.remove(f)

"""
Check for YFRateLimitError
"""
def rate_limited(e):
    for i in e:
        if "YFRateLimitError" in i[1]:
            return True
    return False
    
    
indices = pd.read_excel("Markets_by_Country.xlsx", index_col = 0, header = 0)
looper = list(indices.index)
looper.append('usf')

for i in looper:
       tickers = read_tickers(i)
       t = list(tickers.keys())
       
       # If most recent version of 3y-prices already exists but that of 1y-prices does not
       if os.path.exists(f"prices/3y/{month-1}_{year}/{i}.csv"):
           if os.path.exists(f"prices/1y/{month-1}_{year}/{i}.csv") == False:
              prices = pd.read_csv(f"prices/3y/{month-1}_{year}/{i}.csv").set_index('Date')
              
           else:
               continue

       else:
           j = 0
           # Pull prices, 500 at a time
           while j < int(len(t)/500) + 1:
                 cache_file = f"cache/{i}_{j}.pkl" if len(t) > 500 else f"cache/{i}.pkl"
                 if os.path.exists(cache_file): # Read .pkl file, if already exists
                    p = pd.read_pickle(cache_file)
                       
                 else: 
                     if j != int(len(t)/500):
                        p = pull_prices(t[500*j:500*(j+1)])
                     else:
                        p = pull_prices(t[500*j:])
                     e = list(yf._DownloadCtx.errors.items()) #List of exceptions
                     
                     # Sleep for 2 hours if rate limited
                     if rate_limited(e):
                        time.sleep(7200)
                        continue
                
                     else:
                        p.to_pickle(cache_file) # Cache out prices as .pkl file
                        time.sleep(120) # Sleep for 2 minutes in between calls
                 
                 # Update DataFrame for prices for i
                 if j == 0:
                      prices = p
                      
                 else:
                      prices = prices.merge(p, left_index = True, right_index = True, how = 'left')
                 j += 1 # Move to next set of tickers
                 
           prices = prices[:-1]  # Drop figures for current date             
           remove_cache(i)
 
       prices_one_y = cut_prices(prices, 12) # Cut 1y-prices
       prices.to_csv(f"prices/3y/{month-1}_{year}/{i}.csv")
       prices_one_y.to_csv(f"prices/1y/{month-1}_{year}/{i}.csv")
