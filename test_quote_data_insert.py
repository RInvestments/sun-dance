""" Test script to insert quote data in mongodb

    Author  : Manohar Kuse <mpkuse@connect.ust.hk>
    Created : 8th Jul, 2017
"""
from stockspotter.db.SourceYahoo import SourceYahoo
from collections import OrderedDict
import pymongo
import datetime
import uuid

ticker = '2333.HK'
# ticker = 'ELECTCAST.NSE'
stock_prefix = 'equities_db/data_quotes/'+ticker+'/'
s_yahoo = SourceYahoo( ticker, stock_prefix, 1 )
qqq = s_yahoo.load_quote()

# Setup DB access and file accesses
client = pymongo.MongoClient()
db = client.sun_dance.stock_quotes

# Insert
daily_list = qqq['quotes_daily']
for date_inst in daily_list.keys():
    print date_inst
    adj_close = daily_list[date_inst]['close_adj']
    digest = uuid.uuid3( uuid.NAMESPACE_DNS, str(ticker)+str(date_inst)+str(adj_close) )
    #digest is made of ticker, date and close_adj. so if you try and insert the same data
    # again it will fail, but if there is a split there will be a duplicate entry

    insert_query = {}
    insert_query['id'] = str(digest)
    insert_query['ticker'] = ticker
    insert_query['inserted_on'] = datetime.datetime.now()
    insert_query['datetime'] = datetime.datetime.strptime( date_inst, '%Y-%m-%d')
    for attr in daily_list[date_inst].keys(): #attr will usually be close, close_adj, open, high, low, volume
        print attr
        insert_query[attr] = daily_list[date_inst][attr]

    # print digest
    print insert_query
    try:
        db.insert( insert_query )
    except pymongo.errors.DuplicateKeyError:
        print 'Duplicate Keys error'


# db.insert( {'datetime': datetime.datetime.strptime( '2017-07-08', '%Y-%m-%d'),  'ticker':'2333.HK', 'close':10.48} )
