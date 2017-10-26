## Data acquisition from alphavantage. Provides for NYSE, AMEX, NASDAQ, NSE, HKEX

import sys
import os.path
import urllib2
import time
import code
import string

import json
import urllib2
import os

import TerminalColors
tcol = TerminalColors.bcolors()

import collections
from collections import OrderedDict


class SourceQuotesAlphaVantage:
    def _printer( self, txt ):
        """ """
        print tcol.OKBLUE, 'SourceQuotesAlphaVantage :', tcol.ENDC, txt

    def _debug( self, txt, lvl=0 ):
        """ """
        if lvl in self.verbosity:
            print tcol.OKBLUE, 'SourceQuotesAlphaVantage(Debug) :', tcol.ENDC, txt

    def _report_time( self, txt ):
        """ """
        print tcol.OKBLUE, 'SourceQuotesAlphaVantage(time) :', tcol.ENDC, txt

    def _error( self, txt ):
        """ """
        print tcol.FAIL, 'SourceQuotesAlphaVantage(Error) :', tcol.ENDC, txt



    def __init__(self, ticker, stock_prefix, verbosity=0):
        """ ticker : Stock ticker eg. 2333.HK
        stock_prefix : Storage directory eg. eq_db/data_2016_Dec_09/0175.HK/
        """
        self.verbosity = range(verbosity)


        # print 'constructor'
        self.ticker = ticker
        self.stock_prefix = stock_prefix
        self.priv_dir = stock_prefix + '/quotes_data/'

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

        ticker_seg = self.ticker.split('.')

        xchange = ticker_seg[-1]
        symbol  = '.'.join( ticker_seg[0:-1])
        self._debug( 'xchange: '+xchange )
        self._debug( 'symbol: '+symbol )

        if n>=1000:
            outputsize = 'full'
        else:
            outputsize = 'compact'

        if xchange in ['HK', 'NSE', 'NYSE', 'NASDAQ', 'AMEX' ]:
            # Step-1
            url = self.make_alphavantage_url( symbol, xchange, outputsize )
            file_to_save_raw = self.priv_dir+'/quotes_raw.json'
            self._download_and_save(url, file_to_save_raw, skip_if_exist )

            # Step-2
            file_to_save_parsed = self.priv_dir+'/quotes.json'
            self.__parse_alphavantage( file_to_save_raw, file_to_save_parsed )

            # Step-3
            if rm_raw is True:
                os.remove(file_to_save_raw)
        else:
            self._error( 'Invalid exchange: '+xchange)



        self._report_time( 'Quote Downloaded in %2.4f sec' %(time.time()-startTime) )










    ####### PRIVATE Methods #####################################################
    def make_alphavantage_url( self, symbol, xchange, outputsize ):
        if xchange == 'HK':
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s.HK&apikey=E215Y9QXBIMEAI3B&outputsize=%s' %(symbol, outputsize)
            return url

        if xchange == 'NSE':
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=NSE:%s&apikey=E215Y9QXBIMEAI3B&outputsize=%s' %(symbol, outputsize)
            return url

        if xchange in [ 'NASDAQ', 'NYSE', 'AMEX']:
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&apikey=E215Y9QXBIMEAI3B&outputsize=%s' %(symbol, outputsize)
            return url


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
            # pprint ( json_data )
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
            return
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


    def __parse_alphavantage( self, input_raw_file_name, output_json_file_name ):
        # Takes in the raw file, and processes it to standard format
        self._debug( 'Parsing file %s' %(input_raw_file_name) )
        try:
            data_raw = json.loads( open(input_raw_file_name).read(), object_pairs_hook=OrderedDict )
        except:
            self._error( "No json" )
            return

        if os.path.isfile(input_raw_file_name):
            self._debug( 'File exists, continue parsing it')
        else:
            self._debug( 'Raw downloaded file does not exist, it was probably not downloaded...!')
            self._error( 'Raw downloaded file does not exist, it was probably not downloaded...!')

        output = collections.OrderedDict()

        # Meta Data
        try:
            output['meta'] = collections.OrderedDict()
            output['meta']['ticker'] = data_raw['Meta Data']['2. Symbol']
        except KeyError:
            self._error( 'Cannot parse. Probably alphavantage gave an error' )
            return


        # Quotes
        output['quotes_daily'] = collections.OrderedDict()
        keys = data_raw['Time Series (Daily)'].keys()
        self._debug( 'Data from %s to %s' %(keys[0], keys[-1]) )
        self._printer( 'Data from %s to %s' %(keys[0], keys[-1]) )
        for k in keys: #loop over all dates

            # Get data
            _close = data_raw['Time Series (Daily)'][k]['4. close']
            _close_adj = data_raw['Time Series (Daily)'][k]['5. adjusted close']
            _volume = data_raw['Time Series (Daily)'][k]['6. volume']
            _open = data_raw['Time Series (Daily)'][k]['1. open']
            _low = data_raw['Time Series (Daily)'][k]['3. low']
            _high = data_raw['Time Series (Daily)'][k]['2. high']

            # put data in standard format
            output['quotes_daily'][k] = collections.OrderedDict()
            # output['quotes_daily'][k]['ticker'] = self.ticker
            output['quotes_daily'][k]['close'] = _close
            output['quotes_daily'][k]['close_adj'] = _close_adj
            output['quotes_daily'][k]['volume'] = _volume
            output['quotes_daily'][k]['open'] = _open
            output['quotes_daily'][k]['low'] = _low
            output['quotes_daily'][k]['high'] = _high

            self._debug( "%s:%s" %(k,_close), lvl=2 )

        self._debug( 'Write file %s' %(output_json_file_name) )
        with open( output_json_file_name, "w" ) as handle:
            json_string = json.dumps( output, indent=2 )
            handle.write( json_string )
