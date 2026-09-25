import pandas as pd, os, time, logging
import yfinance as yf
year = time.localtime().tm_year
month = time.localtime().tm_mon

class _RateLimitCatcher(logging.Handler):
    def __init__(self):
        super().__init__(level = logging.ERROR)
        self.hit = False

    def emit(self, record):
        if "YFRateLimitError" in record.getMessage():
            self.hit = True

for i in ['1y', '3y']:
    os.makedirs(f"database/{i}/{month-1}_{year}", exist_ok = True)

for i in ['1y', '3y']:
      files = os.listdir(f"final/{i}/{month-1}_{year}")
      files.remove("markets.csv")
      for f in files:
          returns = pd.read_csv(f"final/{i}/{month-1}_{year}/{f}").set_index('Ticker')
          num_ticks = len(list(returns.index))
          j = 0
          while j < num_ticks:
            yf_logger = logging.getLogger('yfinance')
            catcher = _RateLimitCatcher()
            yf_logger.addHandler(catcher)
            r = returns.index[j]
            try:
               t = yf.Ticker(r)
               info = t.get_info()

            except Exception as e:
               if "YFRateLimitError" in str(e) or "Too Many Requests" in str(e):
                   time.sleep(7200)
                   continue
                
            finally:
               yf_logger.removeHandler(catcher)

            if catcher.hit:
                time.sleep(7200)
                continue
                
            returns.loc[r,'Industry'] = info.get('industry')
            returns.loc[r, 'Sector'] = info.get('sector')
            returns.loc[r, 'Rating'] = info.get('averageAnalystRating')
            j+=1

          returns = returns.reset_index() 
          cols = list(returns.columns)
          a, b = cols.index('Rank'), cols.index('Ticker')
          cols[b], cols[a] = cols[a], cols[b]

          returns = returns[cols]

          returns.to_csv(f"database/{i}/{month-1}_{year}/{f}", index = False)
