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

import time
from datetime import datetime

from bs4 import BeautifulSoup
from yahoo_finance import Share

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

def make_folder_if_not_exist(folder):
    if not os.path.exists(folder):
        print tcol.OKGREEN, 'Make Directory : ', folder, tcol.ENDC
        os.makedirs(folder)
    else:
        print tcol.WARNING, 'Directory already exists : Not creating :', folder, tcol.ENDC


parser = argparse.ArgumentParser()
parser.add_argument( '--hkex', default=False, action='store_true', help='Enable parsing of HKEX data' )
parser.add_argument( '--wsj', default=False, action='store_true', help='Enable parsing of WSJ data' )
parser.add_argument( '--reuters', default=False, action='store_true', help='Enable parsing of Reuters data (people data)' )
parser.add_argument( '--delete_raw', default=False, action='store_true', help='Delete the raw .html after parsing' )
parser.add_argument( '-sd', '--store_dir', required=True, help='Specify database directory (will be created) to store the data' )
parser.add_argument( '-ld', '--lists_db_dir', required=True, help='Specify lists DB directory' )
parser.add_argument( '-v', '--verbosity', type=int, default=0, help='Verbosity 0 is quite. 5 is most verbose' )
args = parser.parse_args()

if args.hkex:
    print tcol.HEADER, 'Enable  : HKEx', tcol.ENDC
else:
    print tcol.HEADER, 'Disable : HKEx', tcol.ENDC

if args.wsj:
    print tcol.HEADER, 'Enable  : WSJ', tcol.ENDC
else:
    print tcol.HEADER, 'Disable : WSJ', tcol.ENDC

if args.reuters:
    print tcol.HEADER, 'Enable  : Reuters', tcol.ENDC
else:
    print tcol.HEADER, 'Disable : Reuters', tcol.ENDC

if args.store_dir:
    print tcol.HEADER, 'store_dir : ', args.store_dir, tcol.ENDC

if args.lists_db_dir:
    print tcol.HEADER, 'store_dir : ', args.lists_db_dir, tcol.ENDC



startTime = time.time()



db_prefix = args.store_dir #'equities_db/data__N'#2017_Feb_26'
if not os.path.exists(db_prefix):
    print tcol.FAIL, 'Non existant database dir : '+db_prefix
    print 'Ensure the directory exists and has the data. Can be downloaded with data_retriver', tcol.ENDC
    quit()


# Get List
lister = TickerLister( args.lists_db_dir )
full_list = lister.list_full_hkex( use_cached=False)

for i,l in enumerate(full_list):
    print tcol.OKGREEN, i,'of %d' %(len(full_list)), l, tcol.ENDC

    # Make Folder if not exist
    folder = db_prefix+'/'+l.ticker+'/'
    make_folder_if_not_exist( folder )


    # Parse HKEX
    if args.hkex:
        s_hkex = SourceHKEXProfile(ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity )
        # s_hkex.download_url(skip_if_exist=not args.force_download)
        s_hkex.parse(delete_raw=args.delete_raw)
        # A = s_hkex.load_hkex_profile()
        # if A is not None:
        #     print A['Industry Classification']


    # Parse WSJ
    if args.wsj:
        s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity )
        # s_wsj.download_url(skip_if_exist=not args.force_download)
        s_wsj.parse(delete_raw=args.delete_raw)
        # # s_wsj.parse_profile()
        # # s_wsj.parse_financials()
        # json_data = s_wsj.load_json_profile()
        # if json_data is not None:
        #     print json_data['Company Info']['Industry'], '-', json_data['Company Info']['Sector']


    # Parse Reuters
    if args.reuters:
        s_reuters = SourceReuters(ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity )
        s_reuters.parse(delete_raw=args.delete_raw)




print tcol.OKGREEN, 'Finished on ', str(datetime.now()), tcol.ENDC
print tcol.OKGREEN, 'Total time : %5.2f sec' %( time.time() - startTime ), tcol.ENDC
