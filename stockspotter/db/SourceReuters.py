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

        UPDATE (30th Mar, 2017)
        Reuters data not as interesting. Will just use its people data (executives)
        for now. In the future possibly news

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

class SourceReuters:
    def _printer( self, txt ):
        """ """
        print tcol.OKBLUE, 'SourceReuters :', tcol.ENDC, txt

    def _debug( self, txt, lvl=0 ):
        """ """
        to_print = self.verbosity
        if lvl in to_print:
            print tcol.OKBLUE, 'SourceReuters(Debug) :', tcol.ENDC, txt

    def _error( self, txt ):
        """ """
        print tcol.FAIL, 'SourceReuters(Error) :', tcol.ENDC, txt

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


    def _rm_if_exists(self, file_path):
        if os.path.exists(file_path):
            self._debug( 'rm ', file_path )
            os.remove( file_path )
            return True
        else:
            self._debug( 'Attempted to remove non-existant raw file : ', file_path)
            return False



    def __init__(self, ticker, stock_prefix, verbosity=0):
        """ ticker : Stock ticker eg. 2333.HK
        stock_prefix : Storage directory eg. eq_db/data_2016_Dec_09/0175.HK/
        """
        self.verbosity = range(verbosity)

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
            self._error( 'File Does not exisits : '+fName )
            return None



    def parse(self, delete_raw=False):
        startTime = time.time()
        self._parse_people(delete_raw=delete_raw)


        self._report_time( 'Parsing done in %4.2fs' %(time.time()-startTime) )



    ############## Company Officers ################
    def _parse_people(self, delete_raw=False):

        # Load Raw html
        raw_html_str = self._load_raw_file( self.priv_dir+'/companyOfficers.html' )
        if raw_html_str is None:
            return


        soup = BeautifulSoup(str(raw_html_str), 'lxml')


        #
        # Column 1 - a) Summary     b) Biographies
        col1 = soup.find( 'div', class_='column1 gridPanel grid8')
        if col1 is not None:
            self._debug( 'Found `column1 gridPanel grid8`', lvl=2)
        else:
            self._error( 'No Data div' )
            return



        col2 = soup.find( 'div', class_='column2 gridPanel grid4')
        if col1 is not None:
            self._debug( 'Found `column2 gridPanel grid4`', lvl=2)
        else:
            self._error( 'No Data div, not writing json file' )
            return



        # eACH COL HAS 2 tables each
        col1_com_news = col1.find_all( 'div', attrs={'id': 'companyNews'} )
        if len(col1_com_news) != 2:
            self._error( 'No Data div-1, not writing json file' )
            return




        col2_com_news = col2.find_all( 'div', attrs={'id': 'companyNews'} )
        if len(col2_com_news) != 2:
            self._error( 'No Data div-1, not writing json file' )
            return



        # get tables
        table_summary = col1_com_news[0].find( 'table', class_='dataTable')
        table_biographies = col1_com_news[1].find( 'table', class_='dataTable')
        table_compensations_basic = col2_com_news[0].find( 'table', class_='dataTable')
        table_compensation_options = col2_com_news[1].find( 'table', class_='dataTable')

        if (table_summary is None) or (table_biographies is None) or (table_compensations_basic is None) or (table_compensation_options is None):
            self._error( 'No Data div-2, not writing json file' )
            return



        #sh,sd etc are named as follows: s==summary, b==biography, cb==compensation basic, co==compensation options
        # h==header, d==2d data table
        sh,sd = self._parse_table(table_summary)
        bh,bd = self._parse_table(table_biographies)
        cbh,cbd = self._parse_table(table_compensations_basic)
        coh,cod = self._parse_table(table_compensation_options)

        #TODO: Assert sd,bd,cbd,cod have same length

        T = Tree()
        for i in range(len(sd)):
            # print sd[i][0], '|', bd[i][0], '|', cbd[i][0], '|', cod[i][0]

            exec_name = str(i) #sd[i][0]
            for j in range(len(sh)):
                T[exec_name][sh[j]] = sd[i][j]

            for j in range(len(bh)):
                T[exec_name][bh[j]] = bd[i][j]

            for j in range(len(cbh)):
                T[exec_name][cbh[j]] = cbd[i][j]

            for j in range(len(coh)):
                T[exec_name][coh[j]] = cod[i][j]



        # Write T as json
        json_fname = self.priv_dir+'/companyExecutives.json'
        json.dump( T, open(json_fname, 'w') )
        self._debug( "JSON File Written : "+json_fname)


        # Delete raw html file (~55Kb each)
        if delete_raw == True:
            self._debug( 'rm '+self.priv_dir+'companyOfficers.html' )
            self._rm_if_exists( self.priv_dir+'companyOfficers.html' )






    def _parse_table(self, table):
        all_tr = table.find_all('tr')

        all_th = all_tr[0].find_all('th')
        # print '# headers : ', len(all_th)
        headers = []
        for th in all_th:
            # print th.text
            headers.append(th.text.strip())





        pt = []
        for tr in all_tr[1:]:
            all_td = tr.find_all('td')
            # print all_td[0].text.strip()
            d = []
            for td in all_td:
                txt = td.text.strip().replace( u'\xa0', ' ')
                d.append(txt.encode('ascii', 'replace'))
            pt.append( d )

        return headers, pt






        #
    ################################################
