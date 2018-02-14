## Tokyo stocks daily data from Quandl
## see: https://www.quandl.com/data/TSE-Tokyo-Stock-Exchange/
##
## BSE
## see: https://www.quandl.com/data/BSE-Bombay-Stock-Exchange/usage/quickstart/api

import sys
import os.path
import urllib2
import time
import datetime
import code
import string

import json
import urllib2
import os

import TerminalColors
tcol = TerminalColors.bcolors()

import collections
from collections import OrderedDict
from bs4 import BeautifulSoup


class SourceQuotesQuandl:
    def __write( self, txt ):
        self.logfile.write( txt +'\n' )

    def _printer( self, txt ):
        """ """
        self.__write( tcol.OKBLUE+ 'SourceQuotesQuandl :'+ tcol.ENDC+ txt )

    def _debug( self, txt, lvl=0 ):
        """ """
        if lvl in self.verbosity:
            self.__write( tcol.OKBLUE+ 'SourceQuotesQuandl(Debug) :'+ tcol.ENDC+ txt )

    def _report_time( self, txt ):
        """ """
        self.__write( tcol.OKBLUE+ 'SourceQuotesQuandl(time) :'+ tcol.ENDC+ txt )

    def _error( self, txt ):
        """ """
        self.__write( tcol.FAIL+ 'SourceQuotesQuandl(Error) :'+ tcol.ENDC+ txt )



    def __init__(self, ticker, stock_prefix, verbosity=0, logfile=None):
        """ ticker : Stock ticker eg. 2333.HK
        stock_prefix : Storage directory eg. eq_db/data_2016_Dec_09/0175.HK/
        """
        self.verbosity = range(verbosity)


        # print 'constructor'
        self.ticker = ticker
        self.stock_prefix = stock_prefix
        self.priv_dir = stock_prefix + '/quotes_data/'

        if logfile is None:
            self.logfile = sys.stdout
        else:
            self.logfile = logfile

        self._debug( 'setting ticker : '+ ticker )
        self._debug( 'setting stock_prefix : '+ stock_prefix )
        self._debug( 'setting priv_dir : '+ self.priv_dir )

        if not os.path.exists(self.priv_dir):
            self._debug( 'Make directory : '+self.priv_dir)
            os.makedirs( self.priv_dir )

    ####### Documentation - Uniform Quote Format #######
        # Standard format for storage of quote data (json)
        #  {
        #         "meta" : {
        #             "ticker" : "2333.HK"
        #         }
        #         "quote_daily" : {
        #             "2017-06-30" : {
        #                 "close" : 2323.3,
        #                 "close_adjusted" :3333,
        #                 "volume" :333333
        #                 "open" : 22,
        #                 "high" : 44,
        #                 "low"  : 32
        #             }
        #             "2017-06-29" : {
        #                 "close" : 2323.3,
        #                 "close_adjusted" :3333,
        #                 "volume" :333333
        #                 "open" : 22,
        #                 "high" : 44,
        #                 "low"  : 32
        #             }
        #             "2017-06-28" : {
        #                 "close" : 2323.3,
        #                 "close_adjusted" :3333,
        #                 "volume" :333333
        #                 "open" : 22,
        #                 "high" : 44,
        #                 "low"  : 32
        #             }
        #             .
        #             .
        #             .
        #         }
        #  }

    ####### Public ######################################################
    ## Attempt to load the .json file. This json file is assumed to be in
    ## Standard format
    def load( self ):
        quote_parsed_file_name = self.priv_dir+'/quotes.json'
        data_json = self._load_json( quote_parsed_file_name )
        return data_json



    ## Will 1. download 2. Parse the downloaded bulk in uniform format 3. Save to disk in uniform format
    def retrive_www( self, n=100, rm_raw=False, skip_if_exist=True ):
        startTime = time.time()
        assert( n > 0 )

        ticker_seg = self.ticker.split('.')

        xchange = ticker_seg[-1]
        symbol  = '.'.join( ticker_seg[0:-1])
        self._debug( 'xchange: '+xchange )
        self._debug( 'symbol: '+symbol )

        if xchange not in ['TYO', 'BSE']:
            self._error( 'This is available only for TYO and BSE. You provided invalid ticker')
            return False

        if n>=1000:
            start_date = None
            end_date = None
        else:
            today = datetime.date.today()
            end_date =  str(today.strftime( '%Y-%m-%d' )) #today's date
            delta = datetime.timedelta( days=n )
            n_days_ago = today - delta
            start_date = str(n_days_ago.strftime( '%Y-%m-%d' ))#date 120 days ago

            self._debug( 'start_date: '+start_date)
            self._debug( 'end_date: '+end_date)

        # Download
        #TODO : Also implement make url with start and end dates, to get 100 days data and/or full data
        if xchange == 'TYO':

            url = self._make_quandl_TSE_url( symbol, xchange, start_date=start_date, end_date=end_date )
        elif xchange == 'BSE':
            url = self._make_quandl_BSE_url( symbol, xchange, start_date=start_date, end_date=end_date )
        else:
            self._error( 'This is available only for TYO and BSE. You provided invalid ticker')
            return False

        self._debug( 'URL : '+url )
        file_to_save_raw = self.priv_dir+'/quotes_raw.json'
        self._download_and_save(url, file_to_save_raw, skip_if_exist )


        # Parse to standard format
        file_to_save_parsed = self.priv_dir+'/quotes.json'

        if xchange == 'TYO':
            self.__parse_quandl_tse( file_to_save_raw, file_to_save_parsed )
        elif xchange == 'BSE':
            self.__parse_quandl_bse( file_to_save_raw, file_to_save_parsed )
        else:
            self._error( 'This is available only for TYO and BSE. You provided invalid ticker')
            return False


        # Remove raw.
        # It is ok to uncomment it. But the disadvantage of it is that. If you need
        # to restart the process. EVerything is downloaded again. Since
        # memory is cheap and not an issue, its keep the raw files
        # if rm_raw is True:
            # os.remove(file_to_save_raw)

        self._report_time( 'Quote Downloaded in %2.4f sec' %(time.time()-startTime) )
        return True







    ####### PRIVATE Methods #####################################################
    def _make_quandl_TSE_url( self, symbol, xchange, start_date=None, end_date=None ):
        # See : https://www.quandl.com/data/TSE-Tokyo-Stock-Exchange/usage/quickstart/api
        if xchange == 'TYO':
            if start_date == None or end_date == None:
                url = 'https://www.quandl.com/api/v3/datasets/TSE/%s?api_key=XJxN-kAGi67W74FRmq3y' %(symbol)
            else:
                url = 'https://www.quandl.com/api/v3/datasets/TSE/%s?start_date=%s&end_date=%s&api_key=XJxN-kAGi67W74FRmq3y' %(symbol, start_date, end_date)
            return url

        self._error( 'This is available only for Tokyo Exchange.' )
        return None

    def _make_quandl_BSE_url( self, symbol, xchange, start_date=None, end_date=None ):
        # See : https://www.quandl.com/data/BSE-Bombay-Stock-Exchange/usage/quickstart/api
        if xchange == 'BSE':
            if start_date == None or end_date == None:
                url = 'https://www.quandl.com/api/v3/datasets/BSE/BOM%s?api_key=XJxN-kAGi67W74FRmq3y' %(symbol)
            else:
                url = 'https://www.quandl.com/api/v3/datasets/BSE/BOM%s?start_date=%s&end_date=%s&api_key=XJxN-kAGi67W74FRmq3y' %(symbol, start_date, end_date)

            return url

        self._error( 'This is available only for Bombay Stock Exchange.' )
        return None

    def _load_json( self, file_name ):
        json_file = file_name
        self._debug( 'Open json_file : %s' %(json_file))

        if os.path.isfile( json_file ):
            self._debug( 'File (%s) exists' %(json_file))
        else:
            self._debug( 'File (%s) does NOT exists' %(json_file))
            self._error( 'File (%s) does NOT exists' %(json_file))
            return None

    	try:
            json_data = json.loads( open( json_file ).read(), object_pairs_hook=OrderedDict )
            return json_data
    	except:
    	    self._error( "no json" )
    	    return None


    def _download_and_save( self, url, fname, skip_if_exist=True ):
        if url is None:
            self._debug( 'URL is None, Skipping...' )
            return False
        self._debug( 'download :'+ url )

        if skip_if_exist and os.path.isfile(fname):
            self._debug( 'File already exists....SKIP')
            return True
        else:
            self._debug( 'File does not exist... continue')


        try:
            self._debug( 'Attempt downloading :'+url)
            html_response = urllib2.urlopen( url )
            with open(fname, "w") as handle:
                hkex_html = html_response.read()
                handle.write( hkex_html )
                self._debug( 'written to : '+ fname )

        except urllib2.HTTPError, e:
            self._printer( 'ERROR : '+str(e) )
            return False
        except urllib2.URLError, e:
            self._printer( 'ERROR : '+str(e) )
            return False


        return True


    def __parse_quandl_tse( self, input_raw_file_name, output_json_file_name ):
        if os.path.isfile(input_raw_file_name):
            self._debug( 'File exists, continue parsing it')
        else:
            self._debug( 'Raw downloaded file does not exist, it was probably not downloaded...!')
            self._error( 'Raw downloaded file does not exist, it was probably not downloaded...!')
            return None


        self._debug( 'Open file for parsing : %s' %(input_raw_file_name) )
        try:
            data_html = open( input_raw_file_name ).read()
            soup = BeautifulSoup( str(data_html), 'lxml' )
            json_tag = soup.find( 'code' )
            json_text = json_tag.text

            data_json = json.loads(json_text, object_pairs_hook=OrderedDict )
            data_json = data_json['dataset']
        except:
            self._error( 'Cannot read the raw quotes file : '+input_raw_file_name+'\nProbably the file is corrupt' )
            return None

        self._debug( 'iterate data_json and writeout in standard format ', 2 )

        output = collections.OrderedDict()
        # Write meta data
        output['meta'] = collections.OrderedDict()
        output['meta']['ticker info'] = data_json['name'].encode( 'ascii', errors='ignore' )
        self._debug( 'Data for '+output['meta']['ticker info'] )

        # Iterate
        output['quotes_daily'] = collections.OrderedDict()
        try:
            self._debug( 'Data from %s to %s' %(data_json['data'][0][0], data_json['data'][-1][0]) )
            self._printer( 'Data from %s to %s' %(data_json['data'][0][0], data_json['data'][-1][0]) )
        except:
            self._error( 'No Quotes data inside' )

        for d in data_json['data']:
            _date =     str(d[0])
            _open =     str(d[1])
            _high =     str(d[2])
            _low =      str(d[3])
            _close =    str(d[4])
            _volume =   str(d[5])
            _close_adj = str("NA in Quandl") # This data is not avaliable with this free dataset

            self._debug( 'date=%s ; close=%s' %(_date, _close), 3 )
            # Std format
            output['quotes_daily'][str(_date)] = collections.OrderedDict()
            output['quotes_daily'][str(_date)]['close'] = _close
            output['quotes_daily'][str(_date)]['close_adj'] = _close_adj
            output['quotes_daily'][str(_date)]['volume'] = _volume
            output['quotes_daily'][str(_date)]['open'] = _open
            output['quotes_daily'][str(_date)]['low'] = _low
            output['quotes_daily'][str(_date)]['high'] = _high



        self._debug( 'Write file %s' %(output_json_file_name) )
        with open( output_json_file_name, "w" ) as handle:
            json_string = json.dumps( output, indent=2 )
            handle.write( json_string )

        return


    def __parse_quandl_bse( self, input_raw_file_name, output_json_file_name ):
        if os.path.isfile(input_raw_file_name):
            self._debug( 'File exists, continue parsing it')
        else:
            self._debug( 'Raw downloaded file does not exist, it was probably not downloaded...!')
            self._error( 'Raw downloaded file does not exist, it was probably not downloaded...!')
            return None


        self._debug( 'Open file for parsing : %s' %(input_raw_file_name) )
        try:
            data_html = open( input_raw_file_name ).read()
            soup = BeautifulSoup( str(data_html), 'lxml' )
            json_tag = soup.find( 'code' )
            json_text = json_tag.text

            data_json = json.loads(json_text, object_pairs_hook=OrderedDict )
            data_json = data_json['dataset']
        except:
            self._error( 'Cannot read the raw quotes file : '+input_raw_file_name+'\nProbably the file is corrupt' )
            return None

        self._debug( 'iterate data_json and writeout in standard format ', 2 )
        output = collections.OrderedDict()
        # Write meta data
        output['meta'] = collections.OrderedDict()
        output['meta']['ticker info'] = data_json['name'].encode( 'ascii', errors='ignore' )
        self._debug( 'Data for '+output['meta']['ticker info'] )

        # Iterate
        output['quotes_daily'] = collections.OrderedDict()
        try:
            self._debug( 'Data from %s to %s' %(data_json['data'][0][0], data_json['data'][-1][0]) )
            self._printer( 'Data from %s to %s' %(data_json['data'][0][0], data_json['data'][-1][0]) )
        except:
            self._error( 'No Quotes.')
        for d in data_json['data']:
            _date =     str(d[0])
            _open =     str(d[1])
            _high =     str(d[2])
            _low =      str(d[3])
            _close =    str(d[4])
            _volume =   str(d[6]) #THIS IS CORRECT. should not be 5 as it is for WAP
            _close_adj = str("NA in Quandl") # This data is not avaliable with this free dataset

            self._debug( 'date=%s ; close=%s' %(_date, _close), 3 )
            # Std format
            output['quotes_daily'][str(_date)] = collections.OrderedDict()
            output['quotes_daily'][str(_date)]['close'] = _close
            output['quotes_daily'][str(_date)]['close_adj'] = _close_adj
            output['quotes_daily'][str(_date)]['volume'] = _volume
            output['quotes_daily'][str(_date)]['open'] = _open
            output['quotes_daily'][str(_date)]['low'] = _low
            output['quotes_daily'][str(_date)]['high'] = _high



        self._debug( 'Write file %s' %(output_json_file_name) )
        with open( output_json_file_name, "w" ) as handle:
            json_string = json.dumps( output, indent=2 )
            handle.write( json_string )

        return
