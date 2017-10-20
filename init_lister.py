
import sys
import os.path
import urllib2

import TerminalColors
tcol = TerminalColors.bcolors()


from stockspotter.lister.TickerLister import TickerLister
from stockspotter.db.SourceWSJ import SourceWSJ
from stockspotter.db.SourceWSJ import URLFactoryWSJ

def print_y( msg ):
    print tcol.WARNING, msg, tcol.ENDC

def print_g( msg ):
    print tcol.OKGREEN, msg, tcol.ENDC


print_y( '-------------------------------------------------')
print_g( '  Initialize Stock Lists from Official sources' )
print_y( '-------------------------------------------------')


lister = TickerLister('equities_db/lists/', 0)
print_y( 'Init HKEX' )
full_list_hkex = lister.list_full_hkex(False)
print 'HKEX: %d stocks' %(len(full_list_hkex))
print_g( 'Done!')

print_y( 'Init India Exchanges - BSE, NSE' )
full_list_bse = lister.list_full_bse(False)
full_list_nse = lister.list_full_nse(False)
print 'BSE: %d stocks' %(len(full_list_bse))
print 'NSE: %d stocks' %(len(full_list_nse))
print_g( 'Done!')

print_y( 'Init USA Exchanges - NYSE, NASDAQ, AMEX')
full_list_nyse = lister.list_full_nyse(False)
full_list_nasdaq = lister.list_full_nasdaq(False)
full_list_amex = lister.list_full_amex(False)
print 'NYSE: %d stocks' %(len(full_list_nyse))
print 'NASDAQ: %d stocks' %(len(full_list_nasdaq))
print 'AMEX: %d stocks' %(len(full_list_amex))
print_g( 'Done!')

print_y( 'Init JPX (Tokyo)')
full_list_tyo = lister.list_full_tyo( False )
print 'TYO: %d stocks' %(len(full_list_tyo))
print_g( 'Done!')


# full_list = full_list_bse[0:3] + full_list_nse[0:3] + full_list_hkex[0:3]
# print full_list



# for l in full_list_nse[0:3]:
#     print l
#     s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix='equities_db/data__i/'+l.ticker, verbosity=1 )
#     s_wsj.download_url()
#     s_wsj.parse()


# s_wsj = SourceWSJ( ticker='AARVEEDEN.NSE', stock_prefix='equities_db/data__i/AARVEEDEN.NSE', verbosity=1 )
# s_wsj.download_url()
# s_wsj.parse()
# import pprint
# pprint.pprint( s_wsj.load_json_profile() )
