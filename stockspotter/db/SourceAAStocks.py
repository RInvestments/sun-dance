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
import json
from bs4 import BeautifulSoup
import pickle

import TerminalColors
tcol = TerminalColors.bcolors()

import collections
import json
def Tree():
    return collections.defaultdict(Tree)

class SourceAAStocks:
    def __write( self, txt ):
        self.logfile.write( txt +'\n' )

    def _printer( self, txt ):
        """ """
        #print tcol.OKBLUE, 'SourceReuters :', tcol.ENDC, txt
        self.__write( tcol.OKBLUE+ 'SourceAAStocks :'+ tcol.ENDC+ txt )

    def _debug( self, txt, lvl=0 ):
        """ """
        to_print = self.verbosity
        if lvl in to_print:
            #print tcol.OKBLUE, 'SourceReuters(Debug) :', tcol.ENDC, txt
            self.__write( tcol.OKBLUE+ 'SourceAAStocks(Debug) :'+ tcol.ENDC+ txt )

    def _error( self, txt ):
        """ """
        #print tcol.FAIL, 'SourceReuters(Error) :', tcol.ENDC, txt
        self.__write( tcol.FAIL+ 'SourceAAStocks(Error) :'+ tcol.ENDC+ txt )

    def _report_time( self, txt ):
        """ """
        #print tcol.OKBLUE, 'SourceReuters(time) :', tcol.ENDC, txt
        self.__write( tcol.OKBLUE+ 'SourceAAStocks(time) :'+ tcol.ENDC+ txt )

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
            return html_response.read()

        except urllib2.HTTPError, e:
            self._printer( 'urllib2.HTTPError : '+str(e) )
            return None
        except urllib2.URLError, e:
            self._printer( 'urllib2.URLError : '+str(e) )
            return None
        except:
            self._printer( 'error in download_and_returnhtml' )
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

        self.xchange = ticker.split('.')[-1]
        self.ticker_p  = '.'.join( ticker.split('.')[0:-1])

        self.priv_dir = stock_prefix + '/aastocks/'

        self._debug( 'setting ticker : '+ ticker )
        self._debug( 'setting stock_prefix : '+ stock_prefix )
        self._debug( 'setting priv_dir : '+ self.priv_dir )



        if not os.path.exists(self.priv_dir):
            self._debug( 'mkdir %s' %(self.priv_dir), lvl=2 )
            os.makedirs( self.priv_dir )

    def download_url( self, skip_if_exist=True ):
        startTime = time.time()
        self.retrive_detailed_company_profile(skip_if_exist=skip_if_exist)
        # Have more calls here as need be

        self._report_time( 'Downloaded in %2.4f sec' %(time.time()-startTime) )


    def retrive_detailed_company_profile(self, skip_if_exist=True):
        """ Get the detailed company profile.
        Sample URL : http://www.aastocks.com/en/stocks/analysis/company-fundamental/company-profile?symbol=2333

        This function saves the file as `self.priv_dir/detailed_company_profile.json`
        """
        #
        # Check Exisitence of Directory (self.priv)
        if not os.path.exists(self.priv_dir):
            self._debug( 'mkdir %s' %(self.priv_dir), lvl=2 )
            os.makedirs( self.priv_dir )
        else:
            self._debug( 'directory %s already exists' %(self.priv_dir), lvl=2 )

        #
        # Check if file exists
        if skip_if_exist and os.path.isfile( self.priv_dir+'/detailed_company_profile.json' ):
            self._debug( "Raw html Exists:" +self.priv_dir+'/detailed_company_profile.json' + "...SKIP" )
            return True

        if self.xchange in ['HK']:
            url = 'http://www.aastocks.com/en/stocks/analysis/company-fundamental/company-profile?symbol=%s' %(self.ticker_p)
        else:
            self._error( 'AAStocks.retrive_detailed_company_profile() on for .HK stocks only')
            return False


        #
        # Download HTTP
        html_response = self._download_and_returnhtml( url )
        # self._download_and_save( url, self.priv_dir+'/prof.html' )

        #
        # Parse with BeautifulSoup
        self._debug( 'Start Parsing')
        soup = BeautifulSoup( str(html_response), 'lxml' )
        grid11 = soup.find( 'div', attrs={'class':'grid_11'} )
        if grid11 is None:
            self._error( 'No data')
            return False

        all_tr = grid11.find_all( 'tr' ) #expect 6 <tr>
        if len(all_tr) != 6:
            self._error( 'Expecting 6 <tr> found %d' %(len(all_tr)) )
            return False

        storage_json = {}
        for tr in all_tr:
            all_td = tr.find_all( 'td' )
            # print '---'
            # print all_td[0].text
            # print all_td[1].text
            storage_json[all_td[0].text] = all_td[1].text

            # print len(all_td)

        #
        # Save JSON
        self._debug( 'Save as json: '+self.priv_dir+'/detailed_company_profile.json')
        with open( self.priv_dir+'/detailed_company_profile.json', 'w') as f:
            json.dump( storage_json, f)





    # def download_url(self, skip_if_exist=True):
    #     """ Having known the ticker and stock_prefix, download the files into the folder """
    #     # mkdir a folder within the stock_prefix (if not exits)
    #     if not os.path.exists(self.priv_dir):
    #         os.makedirs( self.priv_dir )
    #
    #     #TODO: Instead of just checking exisitence of overview, put this code in _download_and_save() to check for exisitence of each file
    #     if skip_if_exist and os.path.isfile( self.priv_dir+'/companyOfficers.html' ):
    #         self._debug( "Raw html Exists:" +self.priv_dir+'/companyOfficers.html' + "...SKIP" )
    #         return True
    #
    #     # Setup the url(s). I care more about 1st 3
    #     # url_overview = 'http://www.reuters.com/finance/stocks/overview?symbol='+self.ticker
    #     # url_financials = 'http://www.reuters.com/finance/stocks/financialHighlights?symbol='+self.ticker
    #     # url_keydev = 'http://www.reuters.com/finance/stocks/'+self.ticker+'/key-developments?pn=1'
    #
    #     # url_companyNews = 'http://www.reuters.com/finance/stocks/companyNews?symbol='+self.ticker
    #     url_companyOfficers = 'http://www.reuters.com/finance/stocks/companyOfficers?symbol='+self.ticker
    #     # url_analyst = 'http://www.reuters.com/finance/stocks/analyst?symbol='+self.ticker
    #
    #     # url_incomeStatement = 'http://www.reuters.com/finance/stocks/incomeStatement?symbol='+self.ticker
    #     # url_incomeStatementAnn = 'http://www.reuters.com/finance/stocks/incomeStatement?perType=ANN&symbol='+self.ticker
    #
    #
    #     # retrive file and write file
    #     startTime = time.time()
    #     self._debug( 'Download : '+url_companyOfficers )
    #     # status_1 = self._download_and_save( url_overview, self.priv_dir+'/overview.html')
    #     # status_2 = self._download_and_save( url_financials, self.priv_dir+'/financials.html')
    #     # status_3 = self._download_and_save( url_keydev, self.priv_dir+'/keydev.html')
    #
    #     # status_4 = self._download_and_save( url_companyNews, self.priv_dir+'/companyNews.html')
    #     status_5 = self._download_and_save( url_companyOfficers, self.priv_dir+'/companyOfficers.html')
    #     # status_6 = self._download_and_save( url_analyst, self.priv_dir+'/analyst.html')
    #
    #     # status_7 = self._download_and_save( url_incomeStatement, self.priv_dir+'/incomeStatement.html')
    #     # status_7 = self._download_and_save( url_incomeStatementAnn, self.priv_dir+'/incomeStatementAnnual.html')
    #
    #     self._report_time( 'Downloaded in %4.2f sec' %(time.time()-startTime) )
