""" Processes the list of equities from HKEX website and just downloads data.
    Downloads
    a) HKEX profile data
    b) Data from Reuters
    c) Data from WSJ

    Sample Usage:
    python data_retriver.py -v 1  -sd equities_db/data__N -ld equities_db/lists --hkex --wsj

"""


import sys
import os.path
# import urllib2
import pprint
import os
import socket

import time
from datetime import datetime

# from bs4 import BeautifulSoup
# from yahoo_finance import Share

import pickle
import argparse

import TerminalColors
tcol = TerminalColors.bcolors()
sys.path.append( os.getcwd() )

# Processor Classes:
from stockspotter.db.SourceHKEXProfile import SourceHKEXProfile
from stockspotter.db.SourceReuters import SourceReuters
from stockspotter.db.SourceYahoo import SourceYahoo
from stockspotter.db.SourceWSJ import SourceWSJ
from stockspotter.db.SourceAAStocks import SourceAAStocks


# Lister class
from stockspotter.lister.TickerLister import TickerLister
def log_write( msg ):
    fp_logfile.write( msg+'\n' )

def log_server( msg ):
    if fp_logserver is not None:
        fp_logserver.sendall( '[%s:%6d:%s] ' %(__file__, os.getpid(), str(datetime.now())) + msg +'\n' )
    # fp_logfile.write( msg+'\n' )


def log_debug( msg, lvl=1 ):
    if lvl in range( args.verbosity ):
        log_write( '[DEBUG=%d]' %(lvl)+msg )

def make_folder_if_not_exist(folder):
    if not os.path.exists(folder):
        # log_write( tcol.OKGREEN+ 'Make Directory : '+ folder+ tcol.ENDC )
        print( tcol.OKGREEN+ 'Make Directory : '+ folder+ tcol.ENDC )
        os.makedirs(folder)
    else:
        # log_write( tcol.WARNING+ 'Directory already exists : Not creating :'+ folder+ tcol.ENDC )
        print( tcol.WARNING+ 'Directory already exists : Not creating :'+ folder+ tcol.ENDC )


parser = argparse.ArgumentParser()
# Source Specific Parsers
# TODO Later have this all in a config file instead of commandline as difference exchanges will have different data sources
parser.add_argument( '--hkex', default=False, action='store_true', help='Enable retrival of HKEX data' )
parser.add_argument( '--wsj', default=False, action='store_true', help='Enable retrival of WSJ data' )
# parser.add_argument( '--yahoo', default=False, action='store_true', help='Enable retrival of Yahoo Quote data (price+volume)' )
parser.add_argument( '--quotes_full', default=False, action='store_true', help='Historical quotes data' )
parser.add_argument( '--quotes_recent', default=False, action='store_true', help='recent 100 days quotes data' )


parser.add_argument( '--reuters', default=False, action='store_true', help='Enable retrival of Reuters company officers data' )
parser.add_argument( '--aastocks', default=False, action='store_true', help='Enable retrival of aastocks data' )

# Bourse
parser.add_argument( '--xhkex', default=False, action='store_true', help='List all HKEX Stocks' )
parser.add_argument( '--xbse', default=False, action='store_true', help='List all Bombay Stock Ex (BSE) Stocks' )
parser.add_argument( '--xnse', default=False, action='store_true', help='List all National Stock Ex India (NSE) Stocks' )
parser.add_argument( '--xnyse', default=False, action='store_true', help='List all New York Stock Exchange Stock (NYSE)' )
parser.add_argument( '--xnasdaq', default=False, action='store_true', help='List all NASDAQ Stocks' )
parser.add_argument( '--xamex', default=False, action='store_true', help='List all AMEX stocks' )
parser.add_argument( '--xtyo', default=False, action='store_true', help='List all Tokyo Ex Stocks' )
parser.add_argument( '--xsse', default=False, action='store_true', help='List all Shanghai Ex Stocks' )
parser.add_argument( '--xszse', default=False, action='store_true', help='List all Shenzen Ex Stocks' )


parser.add_argument( '-f', '--force_download', default=False, action='store_true', help='Force download. Default : False' )
parser.add_argument( '-sd', '--store_dir', required=True, help='Specify database directory (will be created) to store the data' )
parser.add_argument( '-ld', '--lists_db_dir', required=True, help='Specify lists DB directory' )
parser.add_argument(  '--logfile', default=None, help='Logging file name' )
parser.add_argument(  '--logserver', default=None, help='Logging server. eg. localhost:9276' )
parser.add_argument( '-v', '--verbosity', type=int, default=0, help='Verbosity 0 is quite. 5 is most verbose' )
args = parser.parse_args()

db_prefix = args.store_dir #'equities_db/data__N'#2017_Feb_26'
make_folder_if_not_exist( db_prefix )

if args.logfile is None:
    fp_logfile = sys.stdout
else:
    fp_logfile = open( args.logfile, 'w' )
    print 'LOGFILE NAME : ', args.logfile
    log_write( '```\n' + ' '.join( sys.argv ) + '\n```' )


if args.logserver is None:
    fp_logserver = None
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




if args.hkex:
    log_write( tcol.HEADER+ 'Enable  : HKEx'+ tcol.ENDC )
else:
    log_write( tcol.HEADER+ 'Disable : HKEx'+ tcol.ENDC )

if args.wsj:
    log_write( tcol.HEADER+ 'Enable  : WSJ'+ tcol.ENDC )
else:
    log_write( tcol.HEADER+ 'Disable : WSJ'+ tcol.ENDC )



if args.quotes_full:
    log_write( tcol.HEADER+ 'Enable  : Historical Daily Quotes'+ tcol.ENDC )
else:
    log_write( tcol.HEADER+ 'Disable : Historical Daily Quotes'+ tcol.ENDC )

if args.quotes_recent:
    log_write( tcol.HEADER+ 'Enable  : Recent 100d Daily Quotes'+ tcol.ENDC )
else:
    log_write( tcol.HEADER+ 'Disable : Recent 100d Daily Quotes'+ tcol.ENDC )

if args.reuters:
    log_write( tcol.HEADER+ 'Enable  : Reuters'+ tcol.ENDC )
else:
    log_write( tcol.HEADER+ 'Disable : Reuters'+ tcol.ENDC )

if args.store_dir:
    log_write( tcol.HEADER+ 'store_dir : '+ args.store_dir+ tcol.ENDC )


if args.lists_db_dir:
    log_write( tcol.HEADER+ 'lists_db_dir : '+ args.lists_db_dir+ tcol.ENDC )

startTime = time.time()




# Get List
lister = TickerLister( args.lists_db_dir )
full_list = []
n=3
log_write( tcol.HEADER+ ' : Exchanges :'+ tcol.ENDC )
if args.xhkex:
    log_write( tcol.HEADER+ '\t(HKEX) Hong Kong Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_hkex( use_cached=True)#[0:n]
if args.xbse:
    log_write( tcol.HEADER+ '\t(BSE) Bombay Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_bse( use_cached=True )#[0:n]
if args.xnse:
    log_write( tcol.HEADER+ '\t(NSE) National Stock Exchange of India'+ tcol.ENDC )
    full_list += lister.list_full_nse( use_cached=True )#[0:n]
if args.xnyse:
    log_write( tcol.HEADER+ '\t(NYSE) New York Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_nyse( use_cached=True )#[0:n]
if args.xnasdaq:
    log_write( tcol.HEADER+ '\t(NASDAQ) NASDAQ, USA'+ tcol.ENDC )
    full_list += lister.list_full_nasdaq( use_cached=True )#[0:n]
if args.xamex:
    log_write( tcol.HEADER+ '\t(AMEX) American Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_amex( use_cached=True )#[0:n]
if args.xtyo:
    log_write( tcol.HEADER+ '\t(TYO) Japan Exchange Group, Tokyo'+ tcol.ENDC )
    full_list += lister.list_full_tyo( use_cached=True )#[0:n]
if args.xsse:
    log_write( tcol.HEADER+ '\t(SH) Shanghai Stock Exchange, China'+ tcol.ENDC )
    full_list += lister.list_full_sse( use_cached=True )#[0:n]
if args.xszse:
    log_write( tcol.HEADER+ '\t(SZ) Shenzen Stock Exchange, China'+ tcol.ENDC )
    full_list += lister.list_full_szse( use_cached=True )#[0:n]



#
# Main Loop
proc_started = datetime.now()
d_status = False
for i,l in enumerate(full_list):
    log_write( tcol.OKGREEN+ str(i)+' of %d ' %(len(full_list)) + ' '+str(l)+' '+ tcol.ENDC )


    # Make Folder if not exist
    folder = db_prefix+'/'+l.ticker+'/'
    make_folder_if_not_exist( folder )


    # Download HKEX
    if args.hkex:
        s_hkex = SourceHKEXProfile(ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        s_hkex.download_url(skip_if_exist=not args.force_download)
        # s_hkex.parse()
        # A = s_hkex.load_hkex_profile()
        # if A is not None:
        #     print A['Industry Classification']


    # Download WSJ
    if args.wsj:
        s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        d_status = s_wsj.download_url(skip_if_exist=not args.force_download)


    if args.quotes_full:
        s_quotes_historical = SourceYahoo( ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        d_status = s_quotes_historical.download_historical_quote(skip_if_exist=not args.force_download, rm_raw=False)
        #TODO : Add a commandline option for remove raw

    if args.quotes_recent:
        s_quotes_recent100 = SourceYahoo( ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        d_status = s_quotes_recent100.download_recent100d_quote(skip_if_exist=not args.force_download, rm_raw=False)
        #TODO : Add a commandline option for remove raw


    # Download Reuters
    if args.reuters:
        s_reuters = SourceReuters(ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        s_reuters.download_url()

    if args.aastocks:
        s_aastocks = SourceAAStocks( ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        s_aastocks.download_url()

    # Log Server
    if d_status : #print in green if successful, else print in red
        log_server( tcol.OKGREEN+ str(i)+' of %d ' %(len(full_list)) + ' '+str(l)+' '+ tcol.ENDC )
    else:
        log_server( tcol.FAIL+ str(i)+' of %d ' %(len(full_list)) + ' '+str(l)+' '+ tcol.ENDC )


log_write( tcol.OKGREEN+ 'PID: '+ str(os.getpid())+ tcol.ENDC )
log_write( tcol.OKGREEN+ 'Started: '+ str(proc_started)+ tcol.ENDC )
log_write( tcol.OKGREEN+ 'Finished: '+ str(datetime.now())+ tcol.ENDC )
log_write( tcol.OKGREEN+ 'Total time: %5.2f sec' %( time.time() - startTime )+ tcol.ENDC )

log_server( tcol.OKGREEN+ 'Started: '+ str(proc_started)+ tcol.ENDC )
log_server( tcol.OKGREEN+ 'Finished: '+ str(datetime.now())+ tcol.ENDC )
log_server( tcol.OKGREEN+ 'Total time: %5.2f sec' %( time.time() - startTime )+ tcol.ENDC )
