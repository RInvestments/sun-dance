from stockspotter.lister.HSILister import HSILister
from stockspotter.lister.TickerLister import TickerLister
from stockspotter.lister.Taxonomer import Taxonomer

import TerminalColors
tcol = TerminalColors.bcolors()

import time


# hsi = HSILister(lists_db='equities_db/lists/', verbosity=1)
# ticker_list = hsi.search_by_index_name(name='Hang Seng Composite Index')

lister = TickerLister( lists_db='equities_db/lists/' )
full_list = lister.list_full_hkex( use_cached=True )


taxo = Taxonomer(db_prefix='equities_db/data__20170316/', ticker_list=full_list, verbosity=1 )
# taxo.make_industry_tree_wsj()
taxo.make_industry_tree_hkex(add_tickers_to_tree=False)
