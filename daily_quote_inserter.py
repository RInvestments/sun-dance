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

import argparse


from stockspotter.db.SourceYahoo import SourceYahoo
from stockspotter.lister.TickerLister import TickerLister

#----- Commandline Parsing ---#
parser = argparse.ArgumentParser()
parser.add_argument( '-ld', '--lists_db_dir', required=True, help='Specify lists DB directory (eg. equities_db/lists/)' )
parser.add_argument( '-v', '--verbosity', type=int, default=0, help='Verbosity 0 is quite. 5 is most verbose' )
parser.add_argument( '-db', '--quotes_data_dir', required=True, help='Specify quotes directory (eg. equities_db/data_quotes_20170716/)' )

# Bourse
parser.add_argument( '--xhkex', default=False, action='store_true', help='List all HKEX Stocks' )
parser.add_argument( '--xbse', default=False, action='store_true', help='List all Bombay Stock Ex (BSE) Stocks' )
parser.add_argument( '--xnse', default=False, action='store_true', help='List all National Stock Ex India (NSE) Stocks' )

args = parser.parse_args()

if args.lists_db_dir:
    print tcol.HEADER, 'lists_db_dir : ', args.lists_db_dir, tcol.ENDC

if args.quotes_data_dir:
    print tcol.HEADER, 'quotes_data_dir : ', args.quotes_data_dir, tcol.ENDC

# if args.verbosity:
print tcol.HEADER, 'verbosity : ', args.verbosity, tcol.ENDC



# ----------- MAIN -------------#
# Setup DB access and file accesses
client = pymongo.MongoClient()
db = client.sun_dance.stock_quotes #mongodb collection

# # Lister
# # lister = TickerLister( 'equities_db/lists/' )
# lister = TickerLister( args.lists_db_dir )
# full_list = []
# full_list += lister.list_full_hkex( use_cached=True)#[520:]
# # full_list += lister.list_full_bse( use_cached=True )#[1500:]
# full_list += lister.list_full_nse( use_cached=True )

# Get List
lister = TickerLister( args.lists_db_dir )
full_list = []
print tcol.HEADER, ' : Exchanges :', tcol.ENDC
if args.xhkex:
    print tcol.HEADER, '\t(HKEX) Hong Kong Stock Exchange', tcol.ENDC
    full_list += lister.list_full_hkex( use_cached=True)#[0:100]
if args.xbse:
    print tcol.HEADER, '\t(BSE) Bombay Stock Exchange', tcol.ENDC
    full_list += lister.list_full_bse( use_cached=True )#[0:100]
    print tcol.FAIL, 'No quotes data for BSE current TODO. Try without BSE...quiting', tcol.ENDC
    quit()
if args.xnse:
    print tcol.HEADER, '\t(NSE) National Stock Exchange of India', tcol.ENDC
    full_list += lister.list_full_nse( use_cached=True )#[0:100]

# Loop on List
# db_prefix = 'equities_db/data_quotes_20170716/'
db_prefix = args.quotes_data_dir
startTimeTotal = time.time()
for i,l in enumerate(full_list):
    startTime = time.time()
    folder = db_prefix+'/'+l.ticker+'/'
    print tcol.OKGREEN, i,'of %d' %(len(full_list)), l, tcol.ENDC


    s_yahoo = SourceYahoo( l.ticker, folder, args.verbosity )
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
	try:
            insert_query['datetime'] = datetime.datetime.strptime( date_inst, '%Y-%m-%d')
	except ValueError:
	     print 'ValueError, date contains unparsed things. OK to ignore.', insert_query

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
