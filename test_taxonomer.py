from stockspotter.lister.HSILister import HSILister
from stockspotter.lister.Taxonomer import Taxonomer

import TerminalColors
tcol = TerminalColors.bcolors()

import time


hsi = HSILister(lists_db='equities_db/lists/', verbosity=1)
ticker_list = hsi.search_by_index_name(name='Hang Seng Composite Index')


taxo = Taxonomer(db_prefix='equities_db/data__20170316/', ticker_list=ticker_list, verbosity=1 )
taxo.make_industry_tree_wsj()
# taxo.make_industry_tree_hkex() #BUG HERE> this will put just the latest symbol in tree. not all. (issues with this)
