""" Taxonomer - Make a industry tree heirarchy from a list of tickers
        This class takes in a list of tickers. Which is a named tuple
        of type `TickerPoint`. It then converts it into a representation
        based on its industry.

        Later will also have reverse and neighbourhood search on this tree

        Author  : Manohar Kuse <mpkuse@connect.ust.hk>
        Created : 18th Mar, 2017
"""
import sys
import os
import urllib2
import time
import code
import string
import code
import collections
import json

from TickerPoint import TickerPoint
from TickerPoint import TickerTree

from stockspotter.db.SourceWSJ import SourceWSJ
from stockspotter.db.SourceHKEXProfile import SourceHKEXProfile

import TerminalColors
tcol = TerminalColors.bcolors()
tcolor = tcol

class Taxonomer:
    def __init__(self, db_prefix, ticker_list, verbosity=0):
        self.verbosity = range(verbosity)

        self.ticker_list = ticker_list
        self.stocks_db_prefix = db_prefix
        self._debug( 'Taxonomer.__init__ : Input ticker list is of length %d' %(len(ticker_list)) )
        self._debug( 'Setting Taxonomer stocks_db_prefix : '+db_prefix )



    #################### Printer functions ################
    def _printer( self, txt ):
        print tcol.OKBLUE, 'TickerLister :', tcol.ENDC, txt

    def _debug( self, txt, lvl=0 ):
        """ """
        to_print = self.verbosity
        if lvl in to_print:
            print tcol.OKBLUE, 'TickerLister(Debug=%2d) :' %(lvl), tcol.ENDC, txt

    def _error( self, txt ):
        """ """
        print tcol.FAIL, 'TickerLister(Error) :', tcol.ENDC, txt

    def _report_time( self, txt ):
        print tcol.OKBLUE, 'TickerLister(time) :', tcol.ENDC, txt



    ####################
    def make_industry_tree_wsj( self ):
        """ Having known the ticker list, will openup the WSJ data and make heirarchy industry tree """
        tree = TickerTree()
        for i,l in enumerate(self.ticker_list):
            print tcol.OKGREEN, i,l, tcol.ENDC
            s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=self.stocks_db_prefix+'/%s/' %(l.ticker) )
            E = s_wsj.load_json_profile()
            if E is not None:
                sector = E['Company Info']['Sector']
                industry = E['Company Info']['Industry']
                tree[industry][sector] = l.ticker #BUG HERE> this will put just the latest symbol in tree. not all.
            # print E
        code.interact( local=locals() )

    def make_industry_tree_hkex( self ):
        tree = TickerTree()
        for i,l in enumerate(self.ticker_list):
            print tcol.OKGREEN, i,l, tcol.ENDC
            s_hkex = SourceHKEXProfile( ticker=l.ticker, stock_prefix=self.stocks_db_prefix+'/%s/' %(l.ticker) )
            A = s_hkex.load_hkex_profile()
            if A is not None:
                chain = A['Industry Classification'].split( '-' )
                l0 = ' '.join(chain[0].strip().split())
                l1 = ' '.join(chain[1].strip().split())
                l2 = ' '.join(chain[2].strip().split()).split( '(')[0]
                if l2 == None:
                    l2 = ' '.join(chain[2].strip().split())

                tree[l0][l1][l2] = l.ticker #BUG HERE> this will put just the latest symbol in tree. not all. 
        code.interact( local=locals() )
