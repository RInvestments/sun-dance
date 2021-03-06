""" Inserts Daily Quote Data into Mongodb

    Author : Manohar Kuse <mpkuse@connect.ust.hk>
"""

import json
from collections import OrderedDict
import sys
import time
import pymongo
# import datetime
import uuid
import socket
import os
from datetime import datetime
import pprint
import TerminalColors
tcol = TerminalColors.bcolors()

import argparse


from stockspotter.db.SourceYahoo import SourceYahoo
from stockspotter.lister.TickerLister import TickerLister


def __write( msg ):
    # print msg
    fp_logfile.write( msg +'\n')

def log_write( msg ):
    fp_logfile.write( msg+'\n' )

def log_server( msg ):
    if fp_logserver is not None:
        fp_logserver.sendall( '[%s:%6d:%s] ' %(__file__, os.getpid(), str(datetime.now())) + msg +'\n' )
    # fp_logfile.write( msg+'\n' )


#----- Commandline Parsing ---#
parser = argparse.ArgumentParser()
parser.add_argument( '-ld', '--lists_db_dir', required=True, help='Specify lists DB directory (eg. equities_db/lists/)' )
parser.add_argument( '-v', '--verbosity', type=int, default=0, help='Verbosity 0 is quite. 5 is most verbose' )
parser.add_argument( '-db', '--quotes_data_dir', required=True, help='Specify quotes directory (eg. equities_db/data_quotes_20170716/)' )
parser.add_argument(  '--logfile', default=None, help='Logging file name' )
parser.add_argument(  '--logserver', default=None, help='Logging server. eg. localhost:9276' )
parser.add_argument(  '--mongodb', default=None, help='Specify mongodb instance. If not specified will use localhost:27017. eg mongodb://localhost:27017.' )

# Bourse
parser.add_argument( '--xhkex', default=False, action='store_true', help='List all HKEX Stocks' )
parser.add_argument( '--xbse', default=False, action='store_true', help='List all Bombay Stock Ex (BSE) Stocks' )
parser.add_argument( '--xnse', default=False, action='store_true', help='List all National Stock Ex India (NSE) Stocks' )
parser.add_argument( '--xnyse', default=False, action='store_true', help='List all New York Stock Exchange (NYSE) Stocks' )
parser.add_argument( '--xnasdaq', default=False, action='store_true', help='List all NASDAQ Stocks' )
parser.add_argument( '--xamex', default=False, action='store_true', help='List all Amex Stocks' )
parser.add_argument( '--xtyo', default=False, action='store_true', help='List all Japan Exchange (Tokyo) Stocks' )


args = parser.parse_args()

if args.logfile is None:
    fp_logfile = sys.stdout
else:
    fp_logfile = open( args.logfile, 'w' )
    print 'LOGFILE NAME : ', args.logfile
    __write( '```\n' + ' '.join( sys.argv ) + '\n```' )


if args.logserver is None:
    fp_logserver = None
    print 'LOGSERVER    : ', args.logserver
else:
    print 'LOGSERVER    : ', args.logserver
    try:
        _host = args.logserver.split(':')[0]
        _port = int(args.logserver.split(':')[1])
        fp_logserver = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        fp_logserver.connect( (_host,_port) )
        # fp_logserver.sendall( 'Connected!')
        log_server( 'Connected')
    except:
        print tcol.FAIL, 'Cannot connect to logserver', tcol.ENDC
        print 'Start a forked logserver like:'
        print '$ socat TCP4-LISTEN:9595,fork STDOUT'




if args.lists_db_dir:
    __write( tcol.HEADER + 'lists_db_dir : '+ args.lists_db_dir+ tcol.ENDC )

if args.quotes_data_dir:
    __write( tcol.HEADER + 'quotes_data_dir : '+ args.quotes_data_dir+ tcol.ENDC )

# if args.verbosity:
__write( tcol.HEADER + 'verbosity : '+ str(args.verbosity) + tcol.ENDC )



# ----------- MAIN -------------#
# Setup DB access and file accesses
if args.mongodb is None:
    __write( tcol.HEADER + 'Mongo-Server: ' + 'mongodb://localhost:27017/' + tcol.ENDC )
    client = pymongo.MongoClient()
else:
    __write( tcol.HEADER + 'Mongo-Server: ' + args.mongodb +  tcol.ENDC )
    client = pymongo.MongoClient(args.mongodb)

pprint.pprint(  client.server_info()  ) # The process will fail if cannot connect to mongodb
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
n=3
__write( tcol.HEADER+ ' : Exchanges :'+ tcol.ENDC )
if args.xhkex:
    __write( tcol.HEADER+ '\t(HKEX) Hong Kong Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_hkex( use_cached=True)#[0:n]
if args.xbse:
    __write( tcol.HEADER+ '\t(BSE) Bombay Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_bse( use_cached=True )#[0:n]
if args.xnse:
    __write( tcol.HEADER+ '\t(NSE) National Stock Exchange of India'+ tcol.ENDC )
    full_list += lister.list_full_nse( use_cached=True )#[0:n]
if args.xnyse:
    __write( tcol.HEADER+ '\t(NYSE) New York Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_nyse( use_cached=True )#[0:n]
if args.xnasdaq:
    __write( tcol.HEADER+ '\t(NASDAQ) NASDAQ, USA'+ tcol.ENDC )
    full_list += lister.list_full_nasdaq( use_cached=True )#[0:n]
if args.xamex:
    __write( tcol.HEADER+ '\t(AMEX) American Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_amex( use_cached=True )#[0:n]
if args.xtyo:
    __write( tcol.HEADER+ '\t(TYO) Japan Exchange Group, Tokyo'+ tcol.ENDC )
    full_list += lister.list_full_tyo( use_cached=True )#[0:n]



# Loop on List
# db_prefix = 'equities_db/data_quotes_20170716/'
db_prefix = args.quotes_data_dir
startTimeTotal = time.time()
for i,l in enumerate(full_list):
    startTime = time.time()
    folder = db_prefix+'/'+l.ticker+'/'
    __write( tcol.OKGREEN+ str(i)+' of %d ' %(len(full_list))+ str(l)+ tcol.ENDC )
    log_server( tcol.OKGREEN+ str(i)+' of %d ' %(len(full_list))+ str(l)+ tcol.ENDC )


    s_yahoo = SourceYahoo( l.ticker, folder, args.verbosity, fp_logfile )
    q_json_obj = s_yahoo.load_quote()
    if q_json_obj is None:
        __write( tcol.FAIL+ 'No Quote available for '+ l.ticker+ tcol.ENDC )
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
        insert_query['inserted_on'] = datetime.now()
    	try:
            insert_query['datetime'] = datetime.strptime( date_inst, '%Y-%m-%d')
    	except ValueError:
    	     __write( 'ValueError, date contains unparsed things. OK to ignore.'+ str(insert_query) )

        for attr in daily_list[date_inst].keys(): #attr will usually be close, close_adj, open, high, low, volume
            insert_query[attr] = daily_list[date_inst][attr]

        try:
            db.insert( insert_query )
        except pymongo.errors.DuplicateKeyError:
            #'Duplicate Keys error'
            failed_inserts += 1
            # pass
            break;
        except:
            failed_inserts += 1
            #TODO: Consider break here. as soon as you start getting DuplicateKeyErrors means that previous data already exists. Probably no point looking ahead

    try:
        __write( 'Dates : '+ daily_list.keys()[-1]+ '-'+ daily_list.keys()[0]+ ',', )
        __write( 'nPoints : %4d, Failed Inserts : %4d' %( len(daily_list.keys()) , failed_inserts ) )
    except:
        __write( '[Error]daily_list was possibly empty')


    __write( 'Time taken for %s : %4.2fs' %(l.ticker, time.time() - startTime ) )

__write( 'Total Time taken : %4.2fs' %(time.time() - startTimeTotal) )
__write( 'Finished on '+ str(time.ctime()) )

log_server( 'Total Time taken : %4.2fs' %(time.time() - startTimeTotal) )
log_server( 'Finished on '+ str(time.ctime()) )
