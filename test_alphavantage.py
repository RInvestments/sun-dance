## Daily and historical data from :
## https://www.alphavantage.co/


# HISTORICAL
# Sample HK data
#https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=2333.HK&apikey=E215Y9QXBIMEAI3B&outputsize=full

# Sample NSE data
#https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=NSE:TATAMOTORS&apikey=E215Y9QXBIMEAI3B&outputsize=full

from stockspotter.db.SourceYahoo import SourceYahoo


ticker = '6163.HK'
stock_prefix = 'equities_db/data__quotes/'+ticker+'/'
