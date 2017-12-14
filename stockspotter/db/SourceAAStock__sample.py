""" Processor for AAStocks
        This class is to handle aastocks data. This site is ajax based
        and need lot of hacking to get content. Currently will develop
        items as per need basis.

        Basically each public function will download the data and save it
        in json format. There will not be separate parse functions.

            Author  : Manohar Kuse <mpkuse@connect.ust.hk>
            Creared : 14th Dec, 2017
"""
import sys
import os.path
import urllib2
import time
import code
import string

from bs4 import BeautifulSoup
import pickle

import TerminalColors
tcol = TerminalColors.bcolors()

import collections
import json
def Tree():
    return collections.defaultdict(Tree)

class SourceAAStock:
    def __write( self, txt ):
        self.logfile.write( txt +'\n' )

    def _printer( self, txt ):
        """ """
        #print tcol.OKBLUE, 'SourceReuters :', tcol.ENDC, txt
        self.__write( tcol.OKBLUE+ 'SourceAAStock :'+ tcol.ENDC+ txt )

    def _debug( self, txt, lvl=0 ):
        """ """
        to_print = self.verbosity
        if lvl in to_print:
            #print tcol.OKBLUE, 'SourceReuters(Debug) :', tcol.ENDC, txt
            self.__write( tcol.OKBLUE+ 'SourceAAStock(Debug) :'+ tcol.ENDC+ txt )

    def _error( self, txt ):
        """ """
        #print tcol.FAIL, 'SourceReuters(Error) :', tcol.ENDC, txt
        self.__write( tcol.FAIL+ 'SourceAAStock(Error) :'+ tcol.ENDC+ txt )

    def _report_time( self, txt ):
        """ """
        #print tcol.OKBLUE, 'SourceReuters(time) :', tcol.ENDC, txt
        self.__write( tcol.OKBLUE+ 'SourceAAStock(time) :'+ tcol.ENDC+ txt )

    def _download_and_save( self, url, fname ):
        if url is None:
            self._debug( 'URL is None, Skipping...' )
            return False
        self._debug( 'download :'+ url )


        try:
            self._debug( 'Attempt downloading :'+url)
            html_response = urllib2.urlopen( url )
            with open(fname, "w") as handle:
                hkex_html = html_response.read()
                handle.write( hkex_html )
                self._debug( 'written to : '+ fname )

        except urllib2.HTTPError, e:
            self._printer( 'ERROR : '+str(e.code)+':'+e.reason )
            return False
        except urllib2.URLError, e:
            self._printer( 'ERROR : '+str(e.code)+':'+e.reason )
            return False


        return True

    def _download_and_returnhtml( self, url ):
        if url is None:
            self._debug( 'URL is None, Skipping...' )
            return False
        self._debug( 'download :'+ url )


        try:
            self._debug( 'Attempt downloading :'+url)
            html_response = urllib2.urlopen( url )
            return html_response

        except urllib2.HTTPError, e:
            self._printer( 'urllib2.HTTPError : '+str(e) )
            return None
        except urllib2.URLError, e:
            self._printer( 'urllib2.URLError : '+str(e) )
            return None
        except:
            self._printer( 'error in download_and_returnhtml )
            return None


        return None


    def _rm_if_exists(self, file_path):
        if os.path.exists(file_path):
            self._debug( 'rm ', file_path )
            os.remove( file_path )
            return True
        else:
            self._debug( 'Attempted to remove non-existant raw file : ', file_path)
            return False



    def __init__(self, ticker, stock_prefix, verbosity=0, logfile=None ):
        """ ticker : Stock ticker eg. 2333.HK
        stock_prefix : Storage directory eg. eq_db/data_2016_Dec_09/0175.HK/
        """
        self.verbosity = range(verbosity)

        if logfile is None:
            self.logfile = sys.stdout
        else:
            self.logfile = logfile

        # print 'constructor'
        self.ticker = ticker
        self.stock_prefix = stock_prefix
        self.priv_dir = stock_prefix + '/reuters/'
        self.raw_html_str = None

        self._debug( 'setting ticker : '+ ticker )
        self._debug( 'setting stock_prefix : '+ stock_prefix )
        self._debug( 'setting priv_dir : '+ self.priv_dir )

    def download_url(self, skip_if_exist=True):
        """ Having known the ticker and stock_prefix, download the files into the folder """
        # mkdir a folder within the stock_prefix (if not exits)
        if not os.path.exists(self.priv_dir):
            os.makedirs( self.priv_dir )

        #TODO: Instead of just checking exisitence of overview, put this code in _download_and_save() to check for exisitence of each file
        if skip_if_exist and os.path.isfile( self.priv_dir+'/companyOfficers.html' ):
            self._debug( "Raw html Exists:" +self.priv_dir+'/companyOfficers.html' + "...SKIP" )
            return True

        # Setup the url(s). I care more about 1st 3
        # url_overview = 'http://www.reuters.com/finance/stocks/overview?symbol='+self.ticker
        # url_financials = 'http://www.reuters.com/finance/stocks/financialHighlights?symbol='+self.ticker
        # url_keydev = 'http://www.reuters.com/finance/stocks/'+self.ticker+'/key-developments?pn=1'

        # url_companyNews = 'http://www.reuters.com/finance/stocks/companyNews?symbol='+self.ticker
        url_companyOfficers = 'http://www.reuters.com/finance/stocks/companyOfficers?symbol='+self.ticker
        # url_analyst = 'http://www.reuters.com/finance/stocks/analyst?symbol='+self.ticker

        # url_incomeStatement = 'http://www.reuters.com/finance/stocks/incomeStatement?symbol='+self.ticker
        # url_incomeStatementAnn = 'http://www.reuters.com/finance/stocks/incomeStatement?perType=ANN&symbol='+self.ticker


        # retrive file and write file
        startTime = time.time()
        self._debug( 'Download : '+url_companyOfficers )
        # status_1 = self._download_and_save( url_overview, self.priv_dir+'/overview.html')
        # status_2 = self._download_and_save( url_financials, self.priv_dir+'/financials.html')
        # status_3 = self._download_and_save( url_keydev, self.priv_dir+'/keydev.html')

        # status_4 = self._download_and_save( url_companyNews, self.priv_dir+'/companyNews.html')
        status_5 = self._download_and_save( url_companyOfficers, self.priv_dir+'/companyOfficers.html')
        # status_6 = self._download_and_save( url_analyst, self.priv_dir+'/analyst.html')

        # status_7 = self._download_and_save( url_incomeStatement, self.priv_dir+'/incomeStatement.html')
        # status_7 = self._download_and_save( url_incomeStatementAnn, self.priv_dir+'/incomeStatementAnnual.html')

        self._report_time( 'Downloaded in %4.2f sec' %(time.time()-startTime) )
