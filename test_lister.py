
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
# full_list = lister.list_full_bse(True)
full_list = lister.list_full_nse(True)

for l in full_list[0:10]:
    print l
    s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix='equities_db/data__i/'+l.ticker, verbosity=1 )
    s_wsj.download_url()


# s_wsj = SourceWSJ( ticker='AARVEEDEN.NSE', stock_prefix='equities_db/data__i/AARVEEDEN.NSE', verbosity=1 )
# s_wsj.download_url()
# s_wsj.parse()
# import pprint
# pprint.pprint( s_wsj.load_json_profile() )
