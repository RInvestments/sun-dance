""" Test class URLFactoryWSJ """

import sys
import os.path
import urllib2

import TerminalColors
tcol = TerminalColors.bcolors()


from stockspotter.lister.TickerLister import TickerLister
from stockspotter.db.SourceWSJ import SourceWSJ
from stockspotter.db.SourceWSJ import URLFactoryWSJ

ob = URLFactoryWSJ( '4333.TYO' ) #Tokyo
print ob.get_url_financials()
print ob.get_url_wsj_profile()
print ob.get_url_income_statement_q()
print ob.get_url_balance_sheet_q()
print ob.get_url_cash_flow_statement_q()
quit()


# ob = URLFactoryWSJ( 'MMM.NYSE' ) #NYSE
# ob = URLFactoryWSJ( 'ZYNE.NASDAQ' ) #NASDAQ
# ob = URLFactoryWSJ( 'FAX.AMEX' ) #AMEX
# print ob.get_url_financials()
# print ob.get_url_wsj_profile()
# print ob.get_url_income_statement_q()
# print ob.get_url_balance_sheet_q()
# print ob.get_url_cash_flow_statement_q()
quit()


ob = URLFactoryWSJ( '2333.HK' )
print ob.get_url_financials()
print ob.get_url_wsj_profile()
print ob.get_url_income_statement()
print ob.get_url_balance_sheet()
print ob.get_url_cash_flow_statement_q()


ob = URLFactoryWSJ( '500280.BSE' )
print ob.get_url_financials()
print ob.get_url_wsj_profile()
print ob.get_url_income_statement()
print ob.get_url_balance_sheet_q()
print ob.get_url_cash_flow_statement_q()


ob = URLFactoryWSJ( 'ADANIPORTS.NSE' )
print ob.get_url_financials()
print ob.get_url_wsj_profile()
print ob.get_url_income_statement_q()
print ob.get_url_balance_sheet_q()
print ob.get_url_cash_flow_statement_q()
