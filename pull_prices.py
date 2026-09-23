import pandas as pd, yfinance as yf, time, json, os, glob, logging
year = time.localtime().tm_year
month = time.localtime().tm_mon

# Make directories to store prices
for i in ['1y', '3y']:
    os.makedirs(f"prices/{i}/{month-1}_{year}", exist_ok = True)
os.makedirs("cache", exist_ok = True)

"""
Read in tickers for reg
"""
def read_tickers(reg):
    with open(f"tickers/{month-1}_{year}/{reg}.json", 'r') as file:
         tickers = json.load(file)
         
    return tickers

"""
Newer yfinance (1.4.0+) no longer exposes per-ticker download errors on any
public attribute -- yf.shared._ERRORS is dead (the module still exists but
nothing populates it any more) and yf._ERRORS never existed. The only place
yfinance still surfaces a failed download is via its own logger ('yfinance'),
e.g. logger.error("['TICKER']: YFRateLimitError('Too Many Requests. ...')").
This handler watches for that while a download() call runs, in place of the
old yf.shared._ERRORS.items() check.
"""
class _RateLimitCatcher(logging.Handler):
    def __init__(self):
        super().__init__(level = logging.ERROR)
        self.hit = False

    def emit(self, record):
        if "YFRateLimitError" in record.getMessage():
            self.hit = True

"""
Pull 3y-prices for tickers and filter for end-of-month prices only.
Returns (data, was_rate_limited).
"""
def pull_prices(tickers):
    yf_logger = logging.getLogger('yfinance')
    catcher = _RateLimitCatcher()
    yf_logger.addHandler(catcher)
    try:
        data = yf.download(tickers, period = '3y')['Close'].reset_index()
    finally:
        yf_logger.removeHandler(catcher)

    data['Month'] = data['Date'].dt.month
    data['Lead_Month'] = data['Month'].shift(-1)
    data = data[data['Month'] != data['Lead_Month']]
    data = data.drop(['Month', 'Lead_Month'], axis = 1).set_index('Date')
    return data, catcher.hit

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
                        p, hit = pull_prices(t[500*j:500*(j+1)])
                     else:
                        p, hit = pull_prices(t[500*j:])

                     # Sleep for 2 hours if rate limited
                     if hit:
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
