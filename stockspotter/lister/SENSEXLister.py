""" S&P BSE Sensex and its sub-indices.
        Gives methods to retrive constituents of BSE Sensex and its sub-indices.

        Data is retrived from
		http://www.bseindia.com/markets/equity/EQReports/MarketWatch.aspx?expandable=2

        Author  : Manohar Kuse <mpkuse@connect.ust.hk>
        Created : 16th Apr, 2017
"""
import sys
import os
import urllib2
import time
import code
import string
import code
import collections

from TickerPoint import TickerPoint


import TerminalColors
tcol = TerminalColors.bcolors()
tcolor = tcol



class SENSEXLister:
    def __init__(self):
        print "hello world"

    #################### Printer functions ################
    def _printer( self, txt ):
        print tcol.OKBLUE, 'SENSEXLister :', tcol.ENDC, txt

    def _debug( self, txt, lvl=0 ):
        """ """
        to_print = self.verbosity
        if lvl in to_print:
            print tcol.OKBLUE, 'SENSEXLister(Debug=%2d) :' %(lvl), tcol.ENDC, txt

    def _error( self, txt ):
        """ """
        print tcol.FAIL, 'SENSEXLister(Error) :', tcol.ENDC, txt

    def _report_time( self, txt ):
        print tcol.OKBLUE, 'SENSEXLister(time) :', tcol.ENDC, txt

    ####### TODO: Add functions to get all sub-incides. 
