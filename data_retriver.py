""" Processes the list of equities from HKEX website and just downloads data.
    Downloads
    a) HKEX profile data
    b) Data from Reuters
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




startTime = time.time()



db_prefix = 'equities_db/data__'#2017_Feb_26'
make_folder_if_not_exist( db_prefix )


# Get List
lister = TickerLister()
full_list = lister.list_full_hkex()#[0:10]

for i,l in enumerate(full_list):
    # print tcol.OKGREEN, i,l, tcol.ENDC

    # Make Folder if not exist
    folder = db_prefix+'/'+l.ticker+'/'
    # make_folder_if_not_exist( folder )


    # Download HKEX
    s_hkex = SourceHKEXProfile(ticker=l.ticker, stock_prefix=folder )
    # s_hkex.download_url()
    # s_hkex.parse()
    A = s_hkex.load_hkex_profile()
    if A is not None:
        print A['Industry Classification']


    # Download WSJ
    # s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder )
    # # s_wsj.download_url()
    # # s_wsj.parse()
    # # s_wsj.parse_profile()
    # # s_wsj.parse_financials()
    # json_data = s_wsj.load_json_profile()
    # if json_data is not None:
    #     print json_data['Company Info']['Industry'], '-', json_data['Company Info']['Sector']






print tcol.OKGREEN, 'Finished on ', str(datetime.now()), tcol.ENDC
print tcol.OKGREEN, 'Total time : %5.2f sec' %( time.time() - startTime ), tcol.ENDC
