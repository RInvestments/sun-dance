""" This class provides various functions which returns the list of tickers for that category """



import sys
import os.path
import urllib2
import time
import code
import string
import code
import collections

from bs4 import BeautifulSoup
import pickle

import TerminalColors
tcol = TerminalColors.bcolors()
tcolor = tcol

from TickerPoint import TickerPoint

class TickerLister:
    def __init__(self, lists_db):
        self.lists_db = lists_db
        self._debug( "Set lists_db : %s" %(lists_db))


    def _printer( self, txt ):
        print tcol.OKBLUE, 'TickerLister :', tcol.ENDC, txt

    def _debug( self, txt, lvl=0 ):
        """ """
        to_print = []
        if lvl in to_print:
            print tcol.OKBLUE, 'TickerLister(Debug=%2d) :' %(lvl), tcol.ENDC, txt

    def _error( self, txt ):
        """ """
        print tcol.FAIL, 'TickerLister(Error) :', tcol.ENDC, txt

    def _report_time( self, txt ):
        print tcol.OKBLUE, 'TickerLister(time) :', tcol.ENDC, txt

    ########### Full HKEX List ###############
    def list_full_hkex(self, use_cached=True ):
        if use_cached:
            self._debug( 'Retrive from cache : ',self.lists_db+'/eisdeqty.htm' )
            html = open( self.lists_db+'/eisdeqty.htm', 'r').read()
        else:
            # Read URL
            self._debug( 'Download : http://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty.htm' )
            html = urllib2.urlopen('http://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty.htm').read()  # List of securities



        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table', {"class" : 'table_grey_border'} )

        #print out.prettify()
        all_tr = table.find_all( 'tr' )

        # there are 7 td in each tr. 1st row, ie. header row contains 4
        # http://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty_pf.htm

        # rows to process
        si = len(all_tr) - 2
        ticker_list = []
        for i in range(1,si):
            all_td = all_tr[i].find_all( 'td' )
            # print '----'
            ticker = all_td[0].string[1:]+'.HK'
            name = all_td[1].string


            # lot_size = int(all_td[2].string.replace(',',''))

            # print 'Stock Ticker:', ticker
            # print ticker, name
            tmp = TickerPoint( name=name, ticker=ticker)
            ticker_list.append( tmp )
            # print 'Lot size :', lot_size
            # print 'URL : ', hkex_profile_url
            # print 'flags : ', all_td[3].string, all_td[4].string, all_td[5].string, all_td[6].string

        return ticker_list




    ############## Heng Seng Indices #####################
    # https://www.hsi.com.hk/HSI-Net/HSI-Net
    def list_hsi(self):
        q = 0
        #TODO


    ############# Sector Trees ###########################
    # process the sector info and build trees of the market
    #TODO
