# INVESTELITY

___*ACKNOWLEDGEMENT*___ : This project uses [```yfinance```](https://pypi.org/project/yfinance/). The latest version of the module must be installed in any environment, in order to be able to use this repository.

A finance project meant at making it easier for people to make investing decisions around the world, this GitHub repository uses data from YahooFinance to rank and list equities from around the world (for 50 countries) based on historical (1-year and 3-year) risk-adjusted return. One can use this information to build their investment portfolio according to their own preferences for risk, return and volatility.
It comprises the following Python scripts :

1. ___```market_index.py``` :___ To rank stock markets around the world, based on the respective performances of their market indices over the last 1 and 3 years, in terms of risk-adjusted return.
2. ___```pull_tickers.py``` :___ To pull a list of tickers for every equity and US-based fund around the world, listed on YahooFinance. Takes around *15 minutes* to run.
3. ___```pull_prices.py``` :___ To pull daily price data for the past 3 years for all tickers available from YahooFinance. Takes around *24 hours* to run.
4. ___```clean_prices.py``` :____ To drop assets for which the API price call returned erroneous (e.g. negative) data. Takes around *30 minutes* to run.
5. ___```asset_analysis.py``` :___ To calculate annualized return, risk and volatility for each equity and US-based fund (based on both 1-year and 3-year prices) using monthly holding period returns (HPRs), and subsequently rank them on the basis of risk-adjusted return. Takes around *10 minutes* to run.
6. ___```clean_returns.py``` :___ To drop equities and US-based funds with outlier (unrealistic) returns.
7. ___```create_viz.py``` :___ To create Tableau-ready datasets for visualization.
8. ___```add_info.py``` :___ To add information for each stock and fund.

___The package must be run in the above order to ensure an error-free and smooth experience.___ Scripts must not be run more than once a month. Running the package more than once a month will not produce updated results, as returns are calculated on a monthly basis, as of the last trading day in the previous month.
___In order to produce updated results at the beginning of each month, scripts should be run only after the first worldwide trading day in that month has passed.___

This repository also archives all data collected and produced by it in several folders, by date :
1. ___tickers___ : Folder to store ticker symbols and names as .json files, by ISO country code.
2. ___prices___ : Folders to store prices for the last 1 and 3 years respectively, by ISO country code.
3. ___prices_cleaned___ : Folder to store cleaned prices for the last 1 and 3 years, by ISO country code.
4. ___returns___ : Folders to store returns by ISO country code (and for world markets at-large), as according to 1-year or 3-year analyses.
5. ___final___ : Folders to store cleaned returns by ISO country code (and for world markets at-large, as according to 1-year or 3-year analyses. 
6. ____viz____ : Folder to store visualization-ready datasets for equities on Tableau, as according to 1-year or 3-year returns.
7. ____database____ : Folder to store detailed databases (by country) for analysis.

__N.B.:__ This package uses a driver directory ```Markets_by_Country.xlsx``` listing every country's ISO code and market index, which must be accessible to the Python scripts when running them.

A sample of the results that may be produced by this analysis, as visualized on Tableau using script ```create_viz.py``` (as of April 2025), may be found at : [Investelity - Equities](https://public.tableau.com/app/profile/rishabh.basu/viz/Investelity-Equities/Sheet1).

<div class='tableauPlaceholder' id='viz1746880368060' style='position: relative'><noscript><a href='#'><img alt='World Markets (1Y)(As of April 30, 2025)[Go To Funds] ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;6P&#47;6PQZCP6Y4&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='path' value='shared&#47;6PQZCP6Y4' /> <param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;6P&#47;6PQZCP6Y4&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>
