""" This class provides various functions which returns the list of tickers for that category """



import sys
import os.path
import os

import urllib2
from zipfile import ZipFile
import csv

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
    def __init__(self, lists_db, verbosity=0):
        self.verbosity = verbosity
        self._debug( 'Setting Verbosity : %d' %(verbosity) )

        self.lists_db = lists_db
        self.priv_dir = lists_db+'/authoritative_listings/'
        self._debug( "Set priv_dir : %s" %(self.priv_dir))
        self._make_folder_if_not_exist( self.priv_dir )


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


    ############# Helpers ##############
    def _make_folder_if_not_exist(self, folder):
        if not os.path.exists(folder):
            self._debug( 'Make Directory : ' + folder )
            os.mkdir(folder)
        else:
            self._debug( 'Directory already exists : Not creating : ' + folder )


    ########### Full HKEX List ###############
    def list_full_hkex(self, use_cached=True ):
        if use_cached:
            self._debug( 'Retrive from cache : ',self.priv_dir+'/eisdeqty.htm' )
            html = open( self.priv_dir+'/eisdeqty.htm', 'r').read()
            #TODO if there is file not found exception download. for storage create folder hkex
        else:
            # Read URL
            self._debug( 'Download : http://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty.htm' )
            html = urllib2.urlopen('http://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty.htm').read()  # List of securities
            fp = open( self.priv_dir+'/eisdeqty.htm', 'w')
            fp.write( html )
            fp.close()



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




    #TODO : add more official sources for full list of securities.
    ############## India - NSE, BSE ########################
    def list_full_bse(self, use_cached=True):
        # Bhavcopy
        xdir = '/bse/'
        self._make_folder_if_not_exist( self.priv_dir+'/'+xdir )

        if use_cached==False:
            #
            # Download
            # http://www.bseindia.com/download/BhavCopy/Equity/EQ130417_CSV.ZIP
            # Need to modify the date
            url = 'http://www.bseindia.com/download/BhavCopy/Equity/EQ130417_CSV.ZIP'
            response = urllib2.urlopen( url )
            content = response.read()
            f = open(self.priv_dir+xdir+'/bse_bhavcopy.zip', 'w')
            f.write( content )
            f.close()

        #
        # Extract Zip
        z = ZipFile( self.priv_dir+xdir+'/bse_bhavcopy.zip'  )
        fileslist =  z.namelist()
        if len(fileslist) == 1:
            z.extract( fileslist[0], self.priv_dir+xdir )
        else:
            self._error( 'Invalid zip file')
            return None

        #
        # Read CSV
        # In the bhavcopy the columns are as :
        #SC_CODE	SC_NAME	SC_GROUP	SC_TYPE	OPEN	HIGH	LOW	CLOSE	LAST	PREVCLOSE	NO_TRADES	NO_OF_SHRS	NET_TURNOV	TDCLOINDI
        recs = csv.reader( open(self.priv_dir+xdir+fileslist[0]) )
        ticker_list = []
        for r in recs:
            if r[3] == 'Q':
                self._debug( 'symbol: %s ; name: %s' %( r[0], r[1] ) )
                tmp = TickerPoint( ticker='%s.BSE' %(r[0].strip()), name=r[1].strip() )
                ticker_list.append( tmp )

        return ticker_list



    def list_full_nse(self, use_cached=True):
        xdir = '/nse/'
        self._make_folder_if_not_exist( self.priv_dir+'/'+xdir )

        if use_cached == False:
            # Download
            url = 'https://www.nseindia.com/content/historical/EQUITIES/2017/APR/cm13APR2017bhav.csv.zip'
            #TODO: Retrive the zip with urllib2 (basically need to set user agent, if not u get 403, forbidden)
            os.system( 'wget -U "Mozilla" -O %s %s' %(self.priv_dir+xdir+'/nse_bhavcopy.zip',url))


        #
        # Extract Zip
        z = ZipFile( self.priv_dir+xdir+'/nse_bhavcopy.zip'  )
        fileslist =  z.namelist()
        if len(fileslist) == 1:
            z.extract( fileslist[0], self.priv_dir+xdir )
        else:
            self._error( 'Invalid zip file')
            return None

        #
        # Read CSV
        # NSE Bhavcopy :
        #SYMBOL	SERIES	OPEN	HIGH	LOW	CLOSE	LAST	PREVCLOSE	TOTTRDQTY	TOTTRDVAL	TIMESTAMP	TOTALTRADES	ISIN
        recs = csv.reader( open(self.priv_dir+xdir+fileslist[0]) )
        ticker_list = []
        for r in recs:
            if r[1] == 'EQ':
                # print r[0]
                tmp = TickerPoint( ticker='%s.NSE' %(r[0].strip()), name=r[0].strip() )
                ticker_list.append( tmp )

        return ticker_list



    ############## USA - NYSE, NASDAQ ###################


    ############## JAPAN - TYO #########################


    ############# China - SHenzen, Shanghai ################

    ############### Other ASIA - Korea Exchange, Taiwan Stock Exchange,


    ############## Europe - London, Frankfurt, Euronext
