""" Processor for AAStocks
        Sample :
        http://www.reuters.com/finance/stocks/overview?symbol=2333.HK
        http://www.reuters.com/finance/stocks/companyNews?symbol=2333.HK
        http://www.reuters.com/finance/stocks/2333.HK/key-developments?pn=3
        http://www.reuters.com/finance/stocks/companyOfficers?symbol=2333.HK
        http://www.reuters.com/finance/stocks/financialHighlights?symbol=2333.HK
        http://www.reuters.com/finance/stocks/analyst?symbol=2333.HK


        This class will provide function a) download from url, b) load from file if exist
        c) process the dump d) many many getter functions

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

class SourceReuters:
    def _printer( self, txt ):
        """ """
        print tcol.OKBLUE, 'SourceReuters :', tcol.ENDC, txt

    def _debug( self, txt ):
        """ """
        # print tcol.OKBLUE, 'SourceReuters(Debug) :', tcol.ENDC, txt

    def _report_time( self, txt ):
        """ """
        print tcol.OKBLUE, 'SourceReuters(time) :', tcol.ENDC, txt

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

    def __init__(self, ticker, stock_prefix):
        """ ticker : Stock ticker eg. 2333.HK
        stock_prefix : Storage directory eg. eq_db/data_2016_Dec_09/0175.HK/
        """

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
        if skip_if_exist and os.path.isfile( self.priv_dir+'/overview.html' ):
            self._debug( "Raw html Exists:" +self.priv_dir+'/overview.html' + "...SKIP" )
            return True

        # Setup the url(s). I care more about 1st 3
        url_overview = 'http://www.reuters.com/finance/stocks/overview?symbol='+self.ticker
        url_financials = 'http://www.reuters.com/finance/stocks/financialHighlights?symbol='+self.ticker
        url_keydev = 'http://www.reuters.com/finance/stocks/'+self.ticker+'/key-developments?pn=1'

        url_companyNews = 'http://www.reuters.com/finance/stocks/companyNews?symbol='+self.ticker
        url_companyOfficers = 'http://www.reuters.com/finance/stocks/companyOfficers?symbol='+self.ticker
        url_analyst = 'http://www.reuters.com/finance/stocks/analyst?symbol='+self.ticker

        url_incomeStatement = 'http://www.reuters.com/finance/stocks/incomeStatement?symbol='+self.ticker
        url_incomeStatementAnn = 'http://www.reuters.com/finance/stocks/incomeStatement?perType=ANN&symbol='+self.ticker


        # retrive file and write file
        startTime = time.time()
        self._debug( 'Download : '+url_overview )
        status_1 = self._download_and_save( url_overview, self.priv_dir+'/overview.html')
        status_2 = self._download_and_save( url_financials, self.priv_dir+'/financials.html')
        status_3 = self._download_and_save( url_keydev, self.priv_dir+'/keydev.html')

        status_4 = self._download_and_save( url_companyNews, self.priv_dir+'/companyNews.html')
        status_5 = self._download_and_save( url_companyOfficers, self.priv_dir+'/companyOfficers.html')
        status_6 = self._download_and_save( url_analyst, self.priv_dir+'/analyst.html')

        status_7 = self._download_and_save( url_incomeStatement, self.priv_dir+'/incomeStatement.html')
        status_7 = self._download_and_save( url_incomeStatementAnn, self.priv_dir+'/incomeStatementAnnual.html')

        self._report_time( 'Downloaded in %2.4f sec' %(time.time()-startTime) )




    def load_raw_file(self):
        """ Loads the raw html file into variables. To be used by parse() """
        self.raw_overview = self._load_raw_file( self.priv_dir+'/overview.html' )
        self.raw_financials = self._load_raw_file( self.priv_dir+'/financials.html' )
        self.raw_keydev = self._load_raw_file( self.priv_dir+'/keydev.html' )

        self.raw_companyNews = self._load_raw_file( self.priv_dir+'/companyNews.html' )
        self.raw_companyOfficers = self._load_raw_file( self.priv_dir+'/companyOfficers.html' )
        self.raw_analyst = self._load_raw_file( self.priv_dir+'/analyst.html' )

        self.raw_incomeStatement = self._load_raw_file( self.priv_dir+'/incomeStatement.html' )
        self.raw_incomeStatementAnn = self._load_raw_file( self.priv_dir+'/incomeStatementAnnual.html' )


    def _load_raw_file(self, fPath ):
        fName = fPath
        if os.path.isfile( fName ):
            self._debug( 'File exists, load : '+fName )
            raw_html_str = open( fName, 'r' ).read()
            return raw_html_str
        else:
            self._debug( 'File Does not exisits : '+fName )
            return None



    ################### Financials ##############
    def parse_financials(self):
        """ Parse financials """
        soup = BeautifulSoup(str(self.raw_financials), 'lxml')
        mydiv = soup.findAll( "div", {'class' : 'column1 gridPanel grid8'} )
        mydiv_soup = BeautifulSoup( str(mydiv), 'lxml')

        # with open('fname.html', "w") as handle:
            # handle.write( mydiv_soup.prettify() )


        modules = mydiv_soup.findAll( 'div', {'class' : 'module'})
        # There are multiple modules
        for im,mod in enumerate(modules):
            if im==0:
                continue #1st one does not contain any juice
            module_header = mod.find( 'h3' ).get_text().replace('\\n', '').replace('\\r','').replace('\\t','')
            module_table  = mod.find( 'table' )
            print module_header

        code.interact( local=locals() )


    #############################
