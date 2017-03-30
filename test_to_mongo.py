""" Try putting data into mongodb

    Author  : Manohar Kuse <mpkuse@connect.ust.hk
    Created : 27th, Mar, 2017
"""

import json
import collections

import time
from datetime import datetime

from stockspotter.db.SourceHKEXProfile import SourceHKEXProfile
from stockspotter.db.SourceWSJ import SourceWSJ
from stockspotter.db.SourceYahoo import SourceYahoo
from stockspotter.lister.TickerLister import TickerLister

import numpy as np
from tabulate import tabulate

import pymongo
client = pymongo.MongoClient()
db = client.sun_dance

db_prefix = 'equities_db/data__20170316'
list_db_prefix = 'equities_db/lists/'

lister = TickerLister(list_db_prefix)
full_list = lister.list_full_hkex( use_cached=True)


for l in full_list:
    folder = db_prefix+'/'+l.ticker+'/'
    s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder, verbosity=0 )
    s_hkex = SourceHKEXProfile( ticker=l.ticker, stock_prefix=folder, verbosity=0 )

    json_hkex_profile = s_hkex.load_hkex_profile()
    if json_hkex_profile is None:
        continue


    #insert into mongodb
    db.hkex_profile.insert( json_hkex_profile )
