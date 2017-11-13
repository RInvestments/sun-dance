""" This class provides various functions which returns the list of tickers for that category """



import sys
import os.path
import os

import urllib2
import urllib #for GET encoding in sse listing

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

import xlrd #For reading xls and xlsx files
import json


class TickerLister:
    def __init__(self, lists_db, verbosity=0, logfile=None):
        if logfile is None:
            self.logfile = sys.stdout
        else:
            self.logfile = logfile

        self.verbosity = verbosity
        self._debug( 'Setting Verbosity : %d' %(verbosity) )

        self.lists_db = lists_db
        self.priv_dir = lists_db+'/authoritative_listings/'
        self._debug( "Set priv_dir : %s" %(self.priv_dir))
        self._make_folder_if_not_exist( self.priv_dir )

    def __write( self, msg ):
        # print msg
        self.logfile.write( txt +'\n' )



    def _printer( self, txt ):
        self.__write( tcol.OKBLUE+ 'TickerLister :'+ tcol.ENDC+ txt )

    def _debug( self, txt, lvl=0 ):
        """ """
        # to_print = [0,1,2,3,4,5]
        to_print = range(self.verbosity)
        if lvl in to_print:
            self.__write( tcol.OKBLUE+ 'TickerLister(Debug=%2d) :' %(lvl)+ tcol.ENDC+ txt )

    def _error( self, txt ):
        """ """
        self.__write( tcol.FAIL+ 'TickerLister(Error) :'+ tcol.ENDC+ txt )

    def _report_time( self, txt ):
        self.__write( tcol.OKBLUE+ 'TickerLister(time) :'+ tcol.ENDC+ txt )


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


        all_tr = table.find_all( 'tr' )

        # there are 7 td in each tr. 1st row, ie. header row contains 4
        # http://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty_pf.htm

        # rows to process
        si = len(all_tr) - 2
        ticker_list = []
        for i in range(1,si):
            all_td = all_tr[i].find_all( 'td' )
            ticker = all_td[0].string[1:]+'.HK'
            name = all_td[1].string


            # lot_size = int(all_td[2].string.replace(',',''))

            tmp = TickerPoint( name=name, ticker=ticker)
            ticker_list.append( tmp )

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
                tmp = TickerPoint( ticker='%s.NSE' %(r[0].strip()), name=r[0].strip() )
                ticker_list.append( tmp )

        return ticker_list



    ############## USA - NYSE, NASDAQ, AMEX ###################
    def list_full_nyse(self, use_cached=True):
        return self._generic_usa_exchange( xname='NYSE', use_cached=use_cached )

    def list_full_nasdaq(self, use_cached=True):
        return self._generic_usa_exchange( xname='NASDAQ', use_cached=use_cached )

    def list_full_amex(self, use_cached=True):
        return self._generic_usa_exchange( xname='AMEX', use_cached=use_cached )


        # XNAME should be either of : NYSE, NASDAQ, AMEX
    def _generic_usa_exchange(self, xname, use_cached=True):
        if (xname in ['NYSE', 'NASDAQ', 'AMEX']) == False:
            self._error( '_generic_usa_exchange() INVALID xname, should be either of NYSE, NASDAQ or AMEX')
            return None

        xdir = '/%s/' %(xname.lower())
        self._make_folder_if_not_exist( self.priv_dir+'/'+xdir )

        if use_cached == False:
            # Download : http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE
            url = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=%s&render=download' %(xname)
            self._debug( 'Start downloading: %s' %(url) )
            response = urllib2.urlopen( url )
            content = response.read()

            save_filename = self.priv_dir+xdir+'/%s_companylist.csv' %(xname.lower())
            self._debug( 'Writing csv to file : %s' %(save_filename))
            f = open( save_filename, 'w' )
            f.write( content )
            f.close()


        #
        # Read CSV
        # "Symbol","Name","LastSale","MarketCap","ADR TSO","IPOyear","Sector","Industry","Summary Quote"
        # skip the 1st line
        open_filename = self.priv_dir+xdir+'/%s_companylist.csv' %(xname.lower())
        self._debug( 'Open CSV : %s' %(open_filename) )
        try:
            recs = csv.reader( open(open_filename) )
        except IOError:
            self._error( 'Cannot open file : %s\nCannot find the cache file. You might want to try lister.list_full_nyse(False). If issue still persist, raise an issue on github' %(open_filename))
            return None


        next(recs) #skip 1st line which is the header
        ticker_list = []
        for i,r in enumerate(recs):
            self._debug( '%4d] Symbol : %s ; name: %s' %(i,r[0], r[1]), 3)
            tmp = TickerPoint( ticker='%s.%s' %(r[0].strip(), xname),   name=r[1].strip() )
            ticker_list.append( tmp )

        self._debug( 'items:')
        self._debug( str(ticker_list[0]) )
        self._debug( str(ticker_list[1]) )
        self._debug( '...' )
        self._debug( '...' )
        self._debug( str(ticker_list[-2]) )
        self._debug( str(ticker_list[-1]) )
        self._debug( 'return %d items' %(len(ticker_list)) )
        return ticker_list



    ############## JAPAN - TYO #########################
    def list_full_tyo( self, use_cached=True ):
        xdir = '/tyo/'
        self._make_folder_if_not_exist( self.priv_dir+'/'+xdir )

        if use_cached == False:
            # Download
            # http://www.jpx.co.jp/english/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_e.xls
            url = 'http://www.jpx.co.jp/english/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_e.xls'
            self._debug( 'Start downloading: %s' %(url) )
            response = urllib2.urlopen( url )
            content = response.read()

            save_filename = self.priv_dir+xdir+'/tyo_data_e.xls'
            self._debug( 'Writing xls to file : %s' %(save_filename))
            f = open( save_filename, 'w' )
            f.write( content )
            f.close()

        # Process XLS
        open_filename = self.priv_dir+xdir+'/tyo_data_e.xls'
        self._debug( 'Open XLS : '+open_filename )
        xl_workbook = xlrd.open_workbook(open_filename)
        sheet_names = xl_workbook.sheet_names()
        self._debug( 'XLS file containts sheets : %s' %(str(sheet_names)), 2 )

        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

        ticker_list = []
        #skip 1st row
        # [text:u'Effective Date', text:u'Local Code', text:u'Name (English)', text:u'Section/Products', text:u'33 Sector(Code)', text:u'33 Sector(name)', text:u'17 Sector(Code)', text:u'17 Sector(name)', text:u'Size Code (New Index Series)', text:u'Size (New Index Series)']
        for i in range(1,xl_sheet.nrows):
            row = xl_sheet.row(i)
            stock_id = int(row[1].value)
            stock_name = row[2].value
            section = row[3].value

            #skip ETF etc.
            if section in ['Equity Contribution Securities', 'ETFs/ ETNs']:
                self._debug( 'SKIP %d %d %s %s' %(i, stock_id, stock_name, section), 4 )
                pass
            else:
                self._debug( '%d %d %s %s' %(i, stock_id, stock_name, section), 2 )
                tmp = TickerPoint( ticker='%s.TYO' %(str(stock_id).strip()), name=stock_name.strip() )
                ticker_list.append( tmp )



        self._debug( 'items:')
        self._debug( str(ticker_list[0]) )
        self._debug( str(ticker_list[1]) )
        self._debug( '...' )
        self._debug( '...' )
        self._debug( str(ticker_list[-2]) )
        self._debug( str(ticker_list[-1]) )
        self._debug( 'return %d items' %(len(ticker_list)) )
        return ticker_list







    ############# China - SHenzen, Shanghai ################
    def _generic_xls_reading( self, fname ):
        code.interact( local=locals() )
        #TODO

        # XLSX works with openpyxl. But it cannot open xls




    def list_full_sse( self, use_cached=True ): #Shanghai
        xdir = '/sse/'

        self._make_folder_if_not_exist( self.priv_dir+'/'+xdir )

        if use_cached==False:
            # Download
            # curl 'http://query.sse.com.cn/commonQuery.do?jsonCallBack=jQuery111207434857396997545_1509964283162&isPagination=false&sqlId=COMMON_SSE_LISTEDCOMPANIES_COMPANYLIST_EN_L_NEW&pageHelp.pageSize=15&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=11&_=1509964283177' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.8' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36' -H 'Accept: */*' -H 'Referer: http://english.sse.com.cn/products/equities/overview/' -H 'Cookie: yfx_c_g_u_id_10000042=_ck17102913365312697322453131531; VISITED_MENU=%5B%228748%22%2C%228528%22%5D; yfx_f_l_v_t_10000042=f_t_1509255413159__r_t_1509963543299__v_t_1509964560210__r_c_1' -H 'Connection: keep-alive' --compressed

            url = 'http://query.sse.com.cn/commonQuery.do?'
            query_args = { 'jsonCallBack': 'jQuery111207434857396997545_1509964283162',\
                            'isPagination': 'false',\
                            'sqlId': 'COMMON_SSE_LISTEDCOMPANIES_COMPANYLIST_EN_L_NEW',\
                            'pageHelp.pageSize': '15',\
                            'pageHelp.pageNo': '1',\
                            'pageHelp.beginPage': '1',\
                            'pageHelp.cacheSize': '1',\
                            'pageHelp.endPage': '11',\
                            '_': '1509964283177'}
            data = urllib.urlencode( query_args )

            req = urllib2.Request( url+data )
            req.add_header('Accept-Encoding', 'gzip, deflate')
            req.add_header('Accept-Language', 'en-US,en;q=0.8')
            req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36')
            req.add_header('Accept', '*/*')
            req.add_header('Referer', 'http://english.sse.com.cn/products/equities/overview/')
            # req.add_header('Accept': '*/*')
            # req.add_header('Accept': '*/*')

            self._debug( 'Open HTTP request to : '+url )
            try:
                res = urllib2.urlopen( req )
                html = res.read()
            except:
                self._error( 'HTML error when requesting to SSE web' )
                return None

            # Cleapup received raw response
            jj = html.index( '(' )
            html = html[jj+1:-1]

            # Convert to json
            try: #Validate json
                response_json = json.loads( html )
            except:
                self._error( 'Invalid JSON received from SSE. Quit...')
                return None

            save_fname = self.priv_dir+xdir+'/sse_httpresponse.json'
            self._debug( 'Save to file: %s' %(save_fname) )
            f = open( save_fname , 'w' )
            f.write( html )
            f.close()


        # Open file
        open_fname = self.priv_dir+xdir+'/sse_httpresponse.json'
        self._debug( 'Open file : %s' %(open_fname) )
        try:
            fp = open( open_fname )
            json_data = json.loads( fp.read() )
        except IOError:
            self._error( 'Cannot open cached-file containing sse data. You probably want to call this function with use_cached=False. ')
            return None
        except:
            self._error( 'JSON error. Something wrong with cached json file for sse')
            return None

        if 'result' not in json_data.keys():
            self._error( 'The SSE json does not contain \'result\' ' )
            return None

        ticker_list = []
        for en in json_data['result']:
            english_name = en['ENGLISHNAME'].strip()
            stock_ticker = en['PRODUCTID'].strip()
            # Other available keys : SHORTNAME, PRODUCTNAME, PRODUCTID, TEL, WEBSITE, ENGLISHNAME

            # Sometimes no english names
            if english_name == '-':
                english_name = stock_ticker+'.SH'


            self._debug( '%s %s' %(stock_ticker, english_name), 3 )

            tmp = TickerPoint( ticker='%s.SH' %(stock_ticker.strip()), name=english_name.strip() )
            ticker_list.append( tmp )



        self._debug( 'items:')
        self._debug( str(ticker_list[0]) )
        self._debug( str(ticker_list[1]) )
        self._debug( '...' )
        self._debug( '...' )
        self._debug( str(ticker_list[-2]) )
        self._debug( str(ticker_list[-1]) )
        self._debug( 'return %d items' %(len(ticker_list)) )
        return ticker_list






    def list_full_szse(self, use_cached=True ): #Shenzen
        xdir = '/szse/'

        self._make_folder_if_not_exist( self.priv_dir+'/'+xdir )

        if use_cached == False:
            #Download
            url = 'http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1693&tab1PAGENO=1&ENCODE=1&TABKEY=tab1'
            req = urllib2.Request( url )
            req.add_header( 'Referer', 'http://www.szse.cn/main/en/marketdata/stockinformation/' )
            req.add_header( 'Upgrade-Insecure-Requests', '1' )

            response = urllib2.urlopen( req )
            content = response.read()

            save_fname = self.priv_dir+xdir+'/szse_StockInformation.xlsx'
            self._debug( 'Save to file: %s' %(save_fname) )
            f = open( save_fname , 'w' )
            f.write( content )
            f.close()

        open_fname = self.priv_dir+xdir+'/szse_StockInformation.xlsx'
        self._debug( 'Open XLSX file : %s' %(open_fname) )

        xl_workbook = xlrd.open_workbook(open_fname)
        sheet_names = xl_workbook.sheet_names()
        self._debug( 'XLS file containts sheets : %s' %(str(sheet_names)), 2 )

        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

        ticker_list = []
        #skip 1st row
        # [text:u'Effective Date', text:u'Local Code', text:u'Name (English)', text:u'Section/Products', text:u'33 Sector(Code)', text:u'33 Sector(name)', text:u'17 Sector(Code)', text:u'17 Sector(name)', text:u'Size Code (New Index Series)', text:u'Size (New Index Series)']
        for i in range(1,xl_sheet.nrows):
            row = xl_sheet.row(i)
            stock_id = str(row[0].value)
            stock_name = row[1].value

            self._debug( '%s %s' %(stock_id, stock_name), 3 )

            tmp = TickerPoint( ticker='%s.SZ' %(stock_id.strip()), name=stock_name.strip() )
            ticker_list.append( tmp )



        self._debug( 'items:')
        self._debug( str(ticker_list[0]) )
        self._debug( str(ticker_list[1]) )
        self._debug( '...' )
        self._debug( '...' )
        self._debug( str(ticker_list[-2]) )
        self._debug( str(ticker_list[-1]) )
        self._debug( 'return %d items' %(len(ticker_list)) )
        return ticker_list






    ############### Other ASIA - Korea Exchange, Taiwan Stock Exchange,


    ############## Europe - London, Frankfurt, Euronext
    # LSE does not have symbols given
    # deutsche-boerse is doable - vry organized data
    # Euronext - doable need some effort to figure it out
    #http://www.deutsche-boerse-cash-market.com/dbcm-en/instruments-statistics/statistics/listes-companies
