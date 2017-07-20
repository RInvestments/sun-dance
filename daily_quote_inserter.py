""" Inserts Daily Quote Data into Mongodb

    Author : Manohar Kuse <mpkuse@connect.ust.hk>
"""

import json
from collections import OrderedDict

import time
import pymongo
import datetime
import uuid

import TerminalColors
tcol = TerminalColors.bcolors()

from stockspotter.db.SourceYahoo import SourceYahoo
from stockspotter.lister.TickerLister import TickerLister

# ----------- MAIN -------------#
# Setup DB access and file accesses
client = pymongo.MongoClient()
db = client.sun_dance.stock_quotes #mongodb collection

# Lister
lister = TickerLister( 'equities_db/lists/' )
full_list = []
full_list += lister.list_full_hkex( use_cached=True)#[520:]
# full_list += lister.list_full_bse( use_cached=True )#[1500:]
full_list += lister.list_full_nse( use_cached=True )


# Loop on List
db_prefix = 'equities_db/data_quotes_20170716/'
startTimeTotal = time.time()
for i,l in enumerate(full_list):
    startTime = time.time()
    folder = db_prefix+'/'+l.ticker+'/'
    print tcol.OKGREEN, i,'of %d' %(len(full_list)), l, tcol.ENDC


    s_yahoo = SourceYahoo( l.ticker, folder, 1 )
    q_json_obj = s_yahoo.load_quote()
    if q_json_obj is None:
        print tcol.FAIL, 'No Quote available for ', l.ticker, tcol.ENDC
        continue

    #Insert
    daily_list = q_json_obj['quotes_daily']

    failed_inserts = 0
    for date_inst in daily_list.keys():
        adj_close = daily_list[date_inst]['close_adj']
        digest = uuid.uuid3( uuid.NAMESPACE_DNS, str(l.ticker)+str(date_inst)+str(adj_close) )
        #digest is made of ticker, date and close_adj. so if you try and insert the same data
        # again it will fail, but if there is a split there will be a duplicate entry

        insert_query = {}
        insert_query['id'] = str(digest)
        insert_query['ticker'] = l.ticker
        insert_query['inserted_on'] = datetime.datetime.now()
        insert_query['datetime'] = datetime.datetime.strptime( date_inst, '%Y-%m-%d')
        for attr in daily_list[date_inst].keys(): #attr will usually be close, close_adj, open, high, low, volume
            insert_query[attr] = daily_list[date_inst][attr]

        try:
            db.insert( insert_query )
        except pymongo.errors.DuplicateKeyError:
            #print tcol.FAIL, 'Duplicate Keys error', tcol.ENDC
            failed_inserts += 1
            # pass
            break;
            #TODO: Consider break here. as soon as you start getting DuplicateKeyErrors means that previous data already exists. Probably no point looking ahead

    print 'Dates : ', daily_list.keys()[-1], '-', daily_list.keys()[0], ',',
    print 'nPoints : %4d, Failed Inserts : %4d' %( len(daily_list.keys()), failed_inserts )







    print 'Time taken for %s : %4.2fs' %(l.ticker, time.time() - startTime )
print 'Total Time taken : %4.2fs' %(time.time() - startTimeTotal)
