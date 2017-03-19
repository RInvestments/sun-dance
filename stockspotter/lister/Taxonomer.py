""" Taxonomer - Make a industry tree heirarchy from a list of tickers
        This class takes in a list of tickers. Which is a named tuple
        of type `TickerPoint`. It then converts it into a representation
        based on its industry. Uses anytree package

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
# from TickerPoint import TickerTree
from anytree import Node, RenderTree

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
    def _find_in_node_list( self, children_list, to_find ):
        """ Given a list of nodes, find the node named `to_find` """
        for i in children_list:
            if i.name == str(to_find):
                return i

        return None
    def make_industry_tree_wsj( self, add_tickers_to_tree=True ):
        """ Having known the ticker list, will openup the WSJ data and make heirarchy industry tree """
        # tree = TickerTree()
        tree = Node( "root" )
        for i,l in enumerate(self.ticker_list):
            print tcol.OKGREEN, i,l, tcol.ENDC
            s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=self.stocks_db_prefix+'/%s/' %(l.ticker) )
            E = s_wsj.load_json_profile()
            if E is None:
                continue

            sector = str(E['Company Info']['Sector']).replace( '/', ',')
            industry = str(E['Company Info']['Industry']).replace( '/', ',')
            if len(industry) < 3:
                sector = 'Uncategorized'
                industry = 'Uncategorized'


            industry_node = self._find_in_node_list( tree.children, industry )
            if industry_node is None:
                industry_node = Node( industry, parent=tree )


            sector_node = self._find_in_node_list( industry_node.children, sector )
            if sector_node is None:
                sector_node = Node( sector, parent=industry_node )

            # DATA
            if add_tickers_to_tree:
                data_node = self._find_in_node_list( sector_node.children, l.ticker ) #avoid double add, just for safety
                if data_node is None:
                    data_node = Node( l.ticker, parent=sector_node )


        print RenderTree(tree)
        code.interact( local=locals() )

    def make_industry_tree_hkex( self, add_tickers_to_tree=True ):
        treeroot = Node( "root" )
        for i,l in enumerate(self.ticker_list):
            print tcol.OKGREEN, i,l, tcol.ENDC
            #TODO: API Changes needed in Source retrival. stock_prefix must be directory not indivial stock folder
            s_hkex = SourceHKEXProfile( ticker=l.ticker, stock_prefix=self.stocks_db_prefix+'/%s/' %(l.ticker) )
            A = s_hkex.load_hkex_profile()
            if A is None:
                continue

            #TODO: Have a function to clean `chain`. This looks ugly. 
            chain = A['Industry Classification'].split( '-' )
            # print chain
            l0 = ' '.join(chain[0].strip().split())
            l1 = ' '.join(chain[1].strip().split())
            if len(chain) == 3:
                l2 = ' '.join(chain[2].strip().split()).split( '(')[0]
                if l2 == None:
                    l2 = ' '.join(chain[2].strip().split())
            else:
                l2 = 'None'
            l0 = l0.strip()
            l1 = l1.strip()
            l2 = l2.strip()


            l0_node = self._find_in_node_list( treeroot.children, l0 )
            if l0_node is None:
                l0_node = Node( l0, parent=treeroot )

            l1_node = self._find_in_node_list( l0_node.children, l1 )
            if l1_node is None:
                l1_node = Node( l1, parent=l0_node )

            l2_node = self._find_in_node_list( l1_node.children, l2 )
            if l2_node is None:
                l2_node = Node( l2, parent=l1_node )

            # DATA
            if add_tickers_to_tree:
                data_node = self._find_in_node_list( l2_node.children, l.ticker )
                if data_node is None:
                    data_node = Node( l.ticker, parent=l2_node )


            # tree[l0][l1][l2] = l.ticker #BUG HERE> this will put just the latest symbol in tree. not all.


        print RenderTree(treeroot)
        code.interact( local=locals() )
