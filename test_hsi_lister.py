from stockspotter.lister.HSILister import HSILister
import TerminalColors
tcol = TerminalColors.bcolors()

import time

hsi = HSILister(lists_db='equities_db/lists/', verbosity=1)
# hsi.download()
# hsi.download_all_index()

s = time.time()
# ticker_list = hsi.search_by_index_no(no=17)
# ticker_list = hsi.search_by_index_code(code='HSIII')
ticker_list = hsi.search_by_index_name(name='Hang Seng Index')
print 'Search complete in %4.2fms' %( (time.time() - s)*1000.)

for i,l in enumerate(ticker_list):
    print tcol.OKGREEN, i,l, tcol.ENDC

# from stockspotter.lister.TickerLister import TickerLister
# tk = TickerLister( lists_db='equities_db/lists/' )
# L = tk.list_full_hkex()
#
# for l in L:
    # print l
