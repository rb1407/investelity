import pandas as pd, os, time
import yfinance as yf
year = time.localtime().tm_year
month = time.localtime().tm_mon

for i in ['1y', '3y']:
    os.makedirs(f"database/{i}/{month-1}_{year}", exist_ok = True)

for i in ['1y', '3y']:
      files = os.listdir(f"final/{i}/{month-1}_{year}")
      files.remove("markets.csv")
      for f in files:
          returns = pd.read_csv(f"final/{i}/{month-1}_{year}/{f}").set_index('Ticker')
          for r in returns.index:
             t = yf.Ticker(r)
             info = t.get_info()
             returns.loc[r,'Industry'] = info['industry']
             returns.loc[r, 'Sector'] = info['sector']
             returns.loc[r, 'Rating'] = info['averageAnalystRating']

          returns = returns.reset_index() 
          cols = list(returns.columns)
          a, b = cols.index('Rank'), cols.index('Ticker')
          cols[b], cols[a] = cols[a], cols[b]

          returns = returns[cols]

          returns.to_csv(f"database/{i}/{month-1}_{year}/{f}", index = False)
