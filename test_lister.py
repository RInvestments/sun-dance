
import sys
import os.path
import urllib2

import TerminalColors
tcol = TerminalColors.bcolors()


from stockspotter.lister.TickerLister import TickerLister
from stockspotter.db.SourceWSJ import SourceWSJ
from stockspotter.db.SourceWSJ import URLFactoryWSJ


# lister = TickerLister('equities_db/lists/', 1)
# tmp = lister.list_full_hkex(use_cached=True)
# for i,l in enumerate(tmp):
#     print i,l


lister = TickerLister('equities_db/lists/', 1)
full_list_bse = lister.list_full_bse(True)
full_list_nse = lister.list_full_nse(True)
full_list_hkex = lister.list_full_hkex(True)
full_list = full_list_bse[0:3] + full_list_nse[0:3] + full_list_hkex[0:3]

for l in full_list_nse[0:3]:
    print l
    s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix='equities_db/data__i/'+l.ticker, verbosity=1 )
    s_wsj.download_url()
    s_wsj.parse()


# s_wsj = SourceWSJ( ticker='AARVEEDEN.NSE', stock_prefix='equities_db/data__i/AARVEEDEN.NSE', verbosity=1 )
# s_wsj.download_url()
# s_wsj.parse()
# import pprint
# pprint.pprint( s_wsj.load_json_profile() )
