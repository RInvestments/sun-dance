""" Experimenting with Ratio Analysis
        Author  : Manohar Kuse <mpkuse@connect.ust.hk>
        Created : 26th Mar, 2017
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


db_prefix = 'equities_db/data__20170316'
list_db_prefix = 'equities_db/lists/'

lister = TickerLister(list_db_prefix)
full_list = lister.list_full_hkex( use_cached=True)

Shard = collections.namedtuple( 'Shard', 'name ticker price lot_price revenue s_change' )

sha_list = []
for l in full_list:
    folder = db_prefix+'/'+l.ticker+'/'
    s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder, verbosity=0 )
    s_hkex = SourceHKEXProfile( ticker=l.ticker, stock_prefix=folder, verbosity=0 )
    s_yahoo = SourceYahoo( ticker=l.ticker, stock_prefix=folder, verbosity=0 )

    json_wsj_profile = s_wsj.load_json_profile()
    json_hkex_profile = s_hkex.load_hkex_profile()
    json_yahoo = s_yahoo.load_quote()
    if json_wsj_profile is None or json_hkex_profile is None or json_yahoo is None:
        continue
    industry = json_wsj_profile['Company Info']['Industry'].strip()
    sector = json_wsj_profile['Company Info']['Sector'].strip()

    # if industry != "Automotive":
    # if industry != 'Real Estate/Construction':
    # if industry != 'Industrial Goods':
    # if industry != 'Technology':
    # if industry != 'Companies on the Energy Service':
    if industry != 'Financial Services':
    # if industry != 'Telecommunication Services':
    # print sector, l.name
    # if sector != 'Restaurants':
        continue


    try:
        yprice = float(json_yahoo['get_price'])
    except ValueError:
        yprice = 0.0
    except TypeError:
        yprice = 0.0

    # print l.name, l.ticker, share_obj.get_price()
    lot_prix = float(yprice) * float(json_hkex_profile['Board Lot'])
    revenue = json_wsj_profile['Company Info']['Sales or Revenue'].split()
    try :
        _f = revenue[1] if len(revenue) == 2 else 0.0
        if _f == 'B':
            f = 1.0
        if _f == 'T':
            f = 1000.0
        if _f == 'M':
            f = 1E-3

        re=float(revenue[0])*f
    except ValueError:
        re = 0.0
    if re > 10.0:
        sha_list.append( Shard(name=l.name, ticker=l.ticker, price=yprice, lot_price=lot_prix, revenue=re, s_change= json_wsj_profile['Company Info']['1Y Sales Change'] ) )




print tabulate( sorted(sha_list, key=lambda x:x.s_change), headers='keys' )
