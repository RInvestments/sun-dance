""" Parse the downloaded data. For downloading use data_retriver.py
    a) HKEX profile data
    b) Data from Reuters
    c) Data from WSJ

    Sample Usage:
    python data_parser.py --hkex --wsj -sd equities_db/data__N -ld equities_db/lists/ -v 1 --delete_raw

"""


import sys
import os.path
import urllib2
import pprint
import os
import socket

import time
from datetime import datetime

from bs4 import BeautifulSoup
#from yahoo_finance import Share

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


# Lister class
from stockspotter.lister.TickerLister import TickerLister



def log_write( msg ):
    fp_logfile.write( msg+'\n' )

def log_server( msg ):
    if fp_logserver is not None:
        fp_logserver.sendall( '[%s:%6d:%s] ' %(__file__, os.getpid(), str(datetime.now())) + msg +'\n' )
    # fp_logfile.write( msg+'\n' )

def __write( msg ):
    # print msg
    # fp_logfile.write( msg +'\n')
    log_write( msg )

def make_folder_if_not_exist(folder):
    if not os.path.exists(folder):
        __write( tcol.OKGREEN+ 'Make Directory : '+ folder+ tcol.ENDC )
        os.makedirs(folder)
    else:
        __write( tcol.WARNING+ 'Directory already exists : Not creating :'+ folder+ tcol.ENDC )


parser = argparse.ArgumentParser()
# Source Parsers
parser.add_argument( '--hkex', default=False, action='store_true', help='Enable parsing of HKEX data' )
parser.add_argument( '--wsj', default=False, action='store_true', help='Enable parsing of WSJ data' )
parser.add_argument( '--reuters', default=False, action='store_true', help='Enable parsing of Reuters data (people data)' )
parser.add_argument( '--delete_raw_wsj', default=False, action='store_true', help='Delete the raw .html after parsing' )


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


parser.add_argument( '--delete_raw', default=False, action='store_true', help='Delete the raw .html after parsing' )


parser.add_argument( '-sd', '--store_dir', required=True, help='Specify database directory (will be created) to store the data' )
parser.add_argument( '-ld', '--lists_db_dir', required=True, help='Specify lists DB directory' )
parser.add_argument( '-v', '--verbosity', type=int, default=0, help='Verbosity 0 is quite. 5 is most verbose' )
parser.add_argument(  '--logfile', default=None, help='Logging file name' )
parser.add_argument(  '--logserver', default=None, help='Logging server. eg. localhost:9276' )

args = parser.parse_args()

if args.logfile is None:
    fp_logfile = sys.stdout
else:
    fp_logfile = open( args.logfile, 'w' )
    print 'LOGFILE NAME : ', args.logfile
    __write( '```\n' + ' '.join( sys.argv ) + '\n```' )


if args.logserver is None:
    fp_logserver = None
else:
    print 'LOGSERVER    : ', args.logserver
    try:
        _host = args.logserver.split(':')[0]
        _port = int(args.logserver.split(':')[1])
        fp_logserver = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        fp_logserver.connect( (_host,_port) )
        fp_logserver.sendall( 'Connected!')
        log_server( 'Connected')
    except :
        print tcol.FAIL, 'Cannot connect to logserver', tcol.ENDC
        print 'Start a forked logserver like:'
        print '$ socat TCP4-LISTEN:9595,fork STDOUT'




if args.hkex:
    __write( tcol.HEADER+ 'Enable  : HKEx'+ tcol.ENDC )
else:
    __write( tcol.HEADER+ 'Disable : HKEx'+ tcol.ENDC )

if args.wsj:
    __write( tcol.HEADER+ 'Enable  : WSJ'+ tcol.ENDC )
else:
    __write( tcol.HEADER+ 'Disable : WSJ'+ tcol.ENDC )

if args.reuters:
    __write( tcol.HEADER+ 'Enable  : Reuters'+ tcol.ENDC )
else:
    __write( tcol.HEADER+ 'Disable : Reuters'+ tcol.ENDC )

if args.store_dir:
    __write( tcol.HEADER+ 'store_dir : '+ args.store_dir+ tcol.ENDC )

if args.lists_db_dir:
    __write( tcol.HEADER+ 'store_dir : '+ args.lists_db_dir+ tcol.ENDC )



startTime = time.time()



db_prefix = args.store_dir #'equities_db/data__N'#2017_Feb_26'
if not os.path.exists(db_prefix):
    __write( tcol.FAIL+ 'Non existant database dir : '+db_prefix )
    __write( 'Ensure the directory exists and has the data. Can be downloaded with data_retriver'+ tcol.ENDC )
    quit()


# Get List
lister = TickerLister( args.lists_db_dir )
full_list = []
n=3
__write(  tcol.HEADER +' : Exchanges :'+ tcol.ENDC )
if args.xhkex:
    __write(  tcol.HEADER+ '\t(HKEX) Hong Kong Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_hkex( use_cached=True)#[0:n]
if args.xbse:
    __write(  tcol.HEADER+ '\t(BSE) Bombay Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_bse( use_cached=True )#[0:n]
if args.xnse:
    __write(  tcol.HEADER+ '\t(NSE) National Stock Exchange of India'+ tcol.ENDC )
    full_list += lister.list_full_nse( use_cached=True )#[0:n]
if args.xnyse:
    __write(  tcol.HEADER+ '\t(NYSE) New York Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_nyse( use_cached=True )#[0:n]
if args.xnasdaq:
    __write(  tcol.HEADER+ '\t(NASDAQ) NASDAQ, USA'+ tcol.ENDC )
    full_list += lister.list_full_nasdaq( use_cached=True )#[0:n]
if args.xamex:
    __write(  tcol.HEADER+ '\t(AMEX) American Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_amex( use_cached=True )#[0:n]
if args.xtyo:
    __write(  tcol.HEADER+ '\t(TYO) Japan Exchange Group, Tokyo'+ tcol.ENDC )
    full_list += lister.list_full_tyo( use_cached=True )#[0:n]
if args.xsse:
    __write(  tcol.HEADER+ '\t(SH) Shanghai Stock Exchange, China'+ tcol.ENDC )
    full_list += lister.list_full_sse( use_cached=True )#[0:n]
if args.xszse:
    __write(  tcol.HEADER+ '\t(SZ) Shenzen Stock Exchange, China'+ tcol.ENDC )
    full_list += lister.list_full_szse( use_cached=True )#[0:n]

proc_started = datetime.now()
for i,l in enumerate(full_list):
    __write(  tcol.OKGREEN+ str(i)+' of %d ' %(len(full_list))+ str(l) + tcol.ENDC )
    log_server(  tcol.OKGREEN+ str(i)+' of %d ' %(len(full_list))+ str(l) + tcol.ENDC )

    # Make Folder if not exist
    folder = db_prefix+'/'+l.ticker+'/'
    make_folder_if_not_exist( folder )


    # Parse HKEX
    if args.hkex:
        s_hkex = SourceHKEXProfile(ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        s_hkex.parse(delete_raw=args.delete_raw)


    # Parse WSJ
    if args.wsj:
        s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        # s_wsj.parse(delete_raw=args.delete_raw)
        s_wsj.parse(delete_raw=True)


    # Delete WSJ Raw files
    if args.delete_raw_wsj:
        s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        s_wsj.rm_raw()


    # Parse Reuters
    if args.reuters:
        s_reuters = SourceReuters(ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile )
        s_reuters.parse(delete_raw=args.delete_raw)


__write( tcol.OKGREEN+ 'PID: '+ str(os.getpid())+ tcol.ENDC )
__write( tcol.OKGREEN+ 'Started: '+ str(proc_started)+ tcol.ENDC )
__write( tcol.OKGREEN+ 'Finished: '+ str(datetime.now())+ tcol.ENDC )
__write( tcol.OKGREEN+ 'Total time: %5.2f sec' %( time.time() - startTime )+ tcol.ENDC )

log_server( tcol.OKGREEN+ 'Started: '+ str(proc_started)+ tcol.ENDC )
log_server( tcol.OKGREEN+ 'Finished: '+ str(datetime.now())+ tcol.ENDC )
log_server( tcol.OKGREEN+ 'Total time: %5.2f sec' %( time.time() - startTime )+ tcol.ENDC )
