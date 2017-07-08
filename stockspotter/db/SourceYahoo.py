import sys
import os.path
import urllib2
import time
import code
import string

import pickle
import json
import urllib2
import os

import TerminalColors
tcol = TerminalColors.bcolors()

from yahoo_finance import Share
from yahoo_finance import YQLResponseMalformedError

import collections
from collections import OrderedDict

def Tree():
    return collections.defaultdict(Tree)

class SourceYahoo:
    def _printer( self, txt ):
        """ """
        print tcol.OKBLUE, 'SourceYahoo :', tcol.ENDC, txt

    def _debug( self, txt, lvl=0 ):
        """ """
        if lvl in self.verbosity:
            print tcol.OKBLUE, 'SourceYahoo(Debug) :', tcol.ENDC, txt

    def _report_time( self, txt ):
        """ """
        print tcol.OKBLUE, 'SourceYahoo(time) :', tcol.ENDC, txt

    def _error( self, txt ):
        """ """
        print tcol.FAIL, 'SourceYahoo(Error) :', tcol.ENDC, txt


    def _save_obj( self, obj, name ):
        """ Loads a data_dict from pickle """
        with open( name , 'wb') as f:
            self._debug( 'Save :'+name )
            pickle.dump( obj, f, pickle.HIGHEST_PROTOCOL )


    def _load_obj( self, name ):
        with open( name, 'rb' ) as f:
            self._debug( 'Load :'+name )
            return pickle.load(f)


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
            self._printer( 'ERROR : '+str(e.code)+':'+e.reason )
            return False
        except urllib2.URLError, e:
            self._printer( 'ERROR : '+str(e.code)+':'+e.reason )
            return False


        return True


    def __init__(self, ticker, stock_prefix, verbosity=0):
        """ ticker : Stock ticker eg. 2333.HK
        stock_prefix : Storage directory eg. eq_db/data_2016_Dec_09/0175.HK/
        """
        self.verbosity = range(verbosity)


        # print 'constructor'
        self.ticker = ticker
        self.stock_prefix = stock_prefix
        self.priv_dir = stock_prefix + '/yahoo/'
        self.raw_html_str = None

        self._debug( 'setting ticker : '+ ticker )
        self._debug( 'setting stock_prefix : '+ stock_prefix )
        self._debug( 'setting priv_dir : '+ self.priv_dir )

    def load_pickle(self):
        name = self.priv_dir+'/yahoo_dict_data.pk'
        self._debug( 'Open pickle : '+ name )

        if os.path.isfile( name ):
            self._debug( 'Loading : '+name )
            self.data_dict = self._load_obj( name )
        else:
            self._printer( 'File Missing : '+name)
            return False

        return True

    def download_historical_quote(self, skip_if_exist=True ):
        # This now (1st Jul, 2017) does not work
        # self.download_historical_quote_yahoo( skip_if_exist )

        self.download_historical_quote_alphavantage(skip_if_exist)


    def download_historical_quote_alphavantage( self, skip_if_exist=True ):
        if not os.path.exists(self.priv_dir):
            self._debug( 'Make directory : '+self.priv_dir)
            os.makedirs( self.priv_dir )

        # if skip_if_exist and os.path.isfile(output_json_file_name):
        #     self._debug( 'File already exists....SKIP')
        #     return
        # else:
        #     self._debug( 'File does not exist... continue')


        ticker_seg = self.ticker.split('.')

        symbol = ticker_seg[0]
        xchange = ticker_seg[1]


        startTime = time.time()

        # In general, to take advantage of multiple sources,
        # Parse the data to a generic json format.
        ## Step-1 : Download data from a source to a file
        ## Step-2 : Parse the downloaded data into a uniform format
        ## Step-3 : Remove raw file
        #TODO: currently will download the enture 20years data.
        #      Don't need to do this everyday. everyday usually previous 10days
        #      data is enough. This can be switched by the output flag
        outputsize = 'full'
        outputsize = 'compact'

        if xchange == 'HK':

            #sample HK query
            #https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=2333.HK&apikey=E215Y9QXBIMEAI3B&outputsize=full

            # STEP-1
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s.HK&apikey=E215Y9QXBIMEAI3B&outputsize=%s' %(symbol, outputsize)
            file_to_save_raw = self.priv_dir+'/historical_quotes.json'
            self._download_and_save(url, file_to_save_raw, skip_if_exist )

            # Step-2
            file_to_save_parsed = self.priv_dir+'/historical_quotes_parsed.json'
            self.__parse_alphavantage( file_to_save_raw, file_to_save_parsed )

            # Step-3
            os.remove(file_to_save_raw)

            self._report_time( 'Historical Quote Downloaded in %2.4f sec' %(time.time()-startTime) )
            return True

        if xchange == 'NSE':
            # Sample NSE data
            #https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=NSE:TATAMOTORS&apikey=E215Y9QXBIMEAI3B&outputsize=full
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=NSE:%s&apikey=E215Y9QXBIMEAI3B&outputsize=%s' %(symbol,outputsize)
            file_to_save_raw = self.priv_dir+'/historical_quotes.json'
            self._download_and_save(url, file_to_save_raw, skip_if_exist )

            file_to_save_parsed = self.priv_dir+'/historical_quotes_parsed.json'
            self.__parse_alphavantage( file_to_save_raw, file_to_save_parsed )

            #delete raw file
            os.remove(file_to_save_raw)


            self._report_time( 'Historical Quote Downloaded in %2.4f sec' %(time.time()-startTime) )
            return True


        #Example Queries
        # Seem like all this is under construction. However this data is accessible in Yahoo finance ticker format.
        # for example, Hong Kong daily quotes can be obtained as 2333.HK etc. Japan data is not available
        #  <li>Australian Securities Exchange: ASX</li>
        #           https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=ASX:AAC&apikey=E215Y9QXBIMEAI3B
        #   <li>Bombay Stock Exchange: BOM</li>
        #           ?
        #   <li>Borsa Italiana Milan Stock Exchange: BIT</li>
        #   <li>Canadian/Toronto Securities Exchange: TSE</li>
        #           https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSE:AEM&apikey=E215Y9QXBIMEAI3B
        #   <li>Deutsche Borse Frankfurt Stock Exchange: FRA or ETR</li>
        #           https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=ETR:BMW&apikey=E215Y9QXBIMEAI3B
        #   <li>Euronext Amsterdam: AMS</li>
        #   <li>Euronext Brussels: EBR</li>
        #   <li>Euronext Lisbon: ELI</li>
        #   <li>Euronext Paris: EPA</li>
        #   <li>London Stock Exchange: LON</li>
        #   <li>Moscow Exchange: MCX</li>
        #   <li>NASDAQ Exchange: NASDAQ</li>
        #   <li>NASDAQ OMX Copenhagen: CPH</li>
        #   <li>NASDAQ OMX Helsinki: HEL</li>
        #   <li>NASDAQ OMX Iceland: ICE</li>
        #   <li>NASDAQ OMX Stockholm: STO</li>
        #   <li>National Stock Exchange of India: NSE</li>
        #   <li>New York Stock Exchange: NYSE</li>
        #   <li>Singapore Exchange: SGX</li>
        #   <li>Shanghai Stock Exchange: SHA</li>
        #   <li>Shenzhen Stock Exchange: SHE</li>
        #   <li>Taiwan Stock Exchange: TPE</li>
        #   <li>Tokyo Stock Exchange: TYO</li>


        self._error( 'Invalid exchange '+xchange )
        return False







    ## All historical for 10 years listing this file approx 500kb
    ## Yahoo has disabled this service as of 1st Jul, 2017
    def download_historical_quote_yahoo(self, skip_if_exist=True ):
        if not os.path.exists(self.priv_dir):
            self._debug( 'Make directory : '+self.priv_dir)
            os.makedirs( self.priv_dir )

        output_json_file_name = self.priv_dir+'/historical_quotes.json'
        if skip_if_exist and os.path.isfile(output_json_file_name):
            self._debug( 'File already exists....SKIP')
            return
        else:
            self._debug( 'File does not exist... continue')

        # The package is broken for this download.
        # Need to download the raw .csv file. Also note the difference between adj_price and open_price
        # eg:: http://ichart.finance.yahoo.com/table.csv?s=1357.HK&c=1962
        startTime = time.time()

        self._debug( 'retrive url for yahoo historical data : http://ichart.finance.yahoo.com/table.csv?s=0000.HK&c=1962' )

        try:
            historical_csv = urllib2.urlopen('http://ichart.finance.yahoo.com/table.csv?s=%s&c=1962' %(self.ticker)).read()
        except urllib2.HTTPError:
            self._error( 'HTTP Error...SKIP')
            return



        self._debug( 'Open file : '+output_json_file_name )
        fp = open( output_json_file_name, 'w' )

        # The csv is structured into 7 cols, viz. Date, Open, High, Low, Close, Volume, Adj Close (in this order)
        _csv = historical_csv.split('\n')
        # T = Tree()
        fp.write( '{')


        for i,ln in enumerate(_csv[1:-2]):
            cols = ln.split(',')
            if len(cols) != 7: #expecting 7 cols
                continue

            # T[str(i)]['Date'] = cols[0].strip()
            # T[str(i)]['Open'] = cols[1].strip()
            # T[str(i)]['High'] = cols[2].strip()
            # T[str(i)]['Low'] = cols[3].strip()
            # T[str(i)]['Close'] = cols[4].strip()
            # T[str(i)]['Volume'] = cols[5].strip()
            # T[str(i)]['Adj Close'] = cols[6].strip()

            # fp.write( '"%d": ' %(i) + '{\n\t"Date": "%s",\n\t"Open": "%s",\n\t"High": "%s",\n\t"Low": "%s",\n\t"Close": "%s",\n\t"Volume": "%s",\n\t"Adj Close": "%s"\n }\n' \
                        # %( cols[0].strip(), cols[1].strip(), cols[2].strip(),cols[3].strip(), cols[4].strip(), cols[5].strip(), cols[6].strip() )
                    # )

            fp.write( '"%d": ' %(i) + '{"Date": "%s","Open": "%s","High": "%s","Low": "%s","Close": "%s","Volume": "%s","Adj Close": "%s"},' \
                        %( cols[0].strip(), cols[1].strip(), cols[2].strip(),cols[3].strip(), cols[4].strip(), cols[5].strip(), cols[6].strip() )
                    )

        ln = _csv[-2]
        cols = ln.split(',')
        fp.write( '"%d": ' %(i) + '{"Date": "%s","Open": "%s","High": "%s","Low": "%s","Close": "%s","Volume": "%s","Adj Close": "%s"}' \
                    %( cols[0].strip(), cols[1].strip(), cols[2].strip(),cols[3].strip(), cols[4].strip(), cols[5].strip(), cols[6].strip() )
                )

        fp.write( "}")
        fp.close()
        self._debug( 'Written json : '+output_json_file_name )
        self._report_time( 'Historical Quote Downloaded in %2.4f sec' %(time.time()-startTime) )
        # print json.dumps( T, indent=4 )




    ## Quick quote for today
    def download_quick_quote( self ):
        """ Stores only price and volume at datastart to json"""
        if not os.path.exists(self.priv_dir):
            self._debug( 'Make directory : '+self.priv_dir)
            os.makedirs( self.priv_dir )

        startTime = time.time()

        self._debug( 'Query yahoo_finance for '+self.ticker )
        try:
            sh = Share( self.ticker ) #ensure ticker is in yahoo's format
            data_dict = {}

            try:
                data_dict['Volume'] = sh.get_volume()
                data_dict['High'] = sh.get_days_high()
                data_dict['Low'] = sh.get_days_low()
                data_dict['Close'] = sh.get_price()
                data_dict['Open'] = sh.get_open()
                data_dict['Date'] = sh.get_trade_datetime() #eg. 2014-02-05 21:00:00 UTC+0000
            # This is current quote. Not adjusted for splits. This python package is a dumb and does not download split adjusted data.
            # cannot get daily data adjusted. But if downloading hostorical data from url directly
            # http://ichart.finance.yahoo.com/table.csv?s=1357.HK&c=1962 can get the llast column which is split adjusted (i have verified it for apple for example)
            except:
                self._error( 'Data missing error...in download_quick_quote()')



            out_json_filename = self.priv_dir + '/quick_quote.json'
            self._debug( '\n'+ json.dumps( data_dict, indent=4 ) )
            json.dump( data_dict, open(out_json_filename, 'w') )
            self._debug( "File Written : "+out_json_filename)
            self._report_time( 'Quick Quote Downloaded in %2.4f sec' %(time.time()-startTime) )
        except YQLResponseMalformedError:
            self._error( 'YQLResponseMalformedError, not writing json' )



    ## All data for today. Almost never do this,
    ## Deprecated
    def download_data( self, skip_if_exist=True ):
        if not os.path.exists(self.priv_dir):
            self._debug( 'Make directory : '+self.priv_dir)
            os.makedirs( self.priv_dir )

        startTime = time.time()

        if skip_if_exist and os.path.isfile( self.priv_dir+'/yahoo_dict_data.pk' ):
            self._debug( "Pickle Exists...SKIP" )
            return True

        self._debug( 'Query yahoo_finance for '+self.ticker )
        sh = Share( self.ticker )



        data_dict = {}
        data_dict['get_price'] = sh.get_price()
        data_dict['get_change'] = sh.get_change()
        data_dict['get_percent_change'] = sh.get_percent_change()
        data_dict['get_volume'] = sh.get_volume()
        data_dict['get_prev_close'] = sh.get_prev_close()
        data_dict['get_open'] = sh.get_open()
        data_dict['get_avg_daily_volume'] = sh.get_avg_daily_volume()
        data_dict['get_stock_exchange'] = sh.get_stock_exchange()
        data_dict['get_market_cap'] = sh.get_market_cap()
        data_dict['get_book_value'] = sh.get_book_value()
        data_dict['get_ebitda'] = sh.get_ebitda()
        data_dict['get_dividend_share'] = sh.get_dividend_share()
        data_dict['get_dividend_yield'] = sh.get_dividend_yield()
        data_dict['get_earnings_share'] = sh.get_earnings_share()
        data_dict['get_days_high'] = sh.get_days_high()
        data_dict['get_days_low'] = sh.get_days_low()
        data_dict['get_year_high'] = sh.get_year_high()
        data_dict['get_year_low'] = sh.get_year_low()
        data_dict['get_50day_moving_avg'] = sh.get_50day_moving_avg()
        data_dict['get_200day_moving_avg'] = sh.get_200day_moving_avg()
        data_dict['get_price_earnings_ratio'] = sh.get_price_earnings_ratio()
        data_dict['get_price_earnings_growth_ratio'] = sh.get_price_earnings_growth_ratio()
        data_dict['get_price_sales'] = sh.get_price_sales()
        data_dict['get_price_book'] = sh.get_price_book()
        data_dict['get_short_ratio'] = sh.get_short_ratio()
        # data_dict['get_trade_datetime'] = sh.get_trade_datetime()
        data_dict['get_name'] = sh.get_name()
        data_dict['get_percent_change_from_year_high'] = sh.get_percent_change_from_year_high()
        data_dict['get_percent_change_from_year_low'] = sh.get_percent_change_from_year_low()
        data_dict['get_change_from_year_low'] = sh.get_change_from_year_low()
        data_dict['get_change_from_year_high'] = sh.get_change_from_year_high()
        data_dict['get_percent_change_from_200_day_moving_average'] = sh.get_percent_change_from_200_day_moving_average()
        data_dict['get_change_from_200_day_moving_average'] = sh.get_change_from_200_day_moving_average()
        data_dict['get_percent_change_from_50_day_moving_average'] = sh.get_percent_change_from_50_day_moving_average()
        data_dict['get_change_from_50_day_moving_average'] = sh.get_change_from_50_day_moving_average()
        data_dict['get_EPS_estimate_next_quarter'] = sh.get_EPS_estimate_next_quarter()
        data_dict['get_EPS_estimate_next_year'] = sh.get_EPS_estimate_next_year()
        data_dict['get_ex_dividend_date'] = sh.get_ex_dividend_date()
        data_dict['get_EPS_estimate_current_year'] = sh.get_EPS_estimate_current_year()
        data_dict['get_price_EPS_estimate_next_year'] = sh.get_price_EPS_estimate_next_year()
        data_dict['get_price_EPS_estimate_current_year'] = sh.get_price_EPS_estimate_current_year()
        data_dict['get_one_yr_target_price'] = sh.get_one_yr_target_price()
        data_dict['get_change_percent_change'] = sh.get_change_percent_change()
        data_dict['get_dividend_pay_date'] = sh.get_dividend_pay_date()
        data_dict['get_currency'] = sh.get_currency()
        data_dict['get_last_trade_with_time'] = sh.get_last_trade_with_time()
        data_dict['get_days_range'] = sh.get_days_range()
        data_dict['get_year_range'] = sh.get_year_range()

        obj_name = self.priv_dir + '/yahoo_dict_data.pk'
        self._save_obj(data_dict, obj_name)

        out_json_filename = self.priv_dir + '/quote_detailed.json'
        self._debug( '\n'+ json.dumps( data_dict, indent=4 ) , lvl=2 )
        json.dump( data_dict, open(out_json_filename, 'w') )
        self._debug( "File Written : "+out_json_filename)
        self._report_time( 'Downloaded in %2.4f sec' %(time.time()-startTime) )


    ############################### LOAD JSON ########################
    def _load_json( self, file_name ):
        json_file = file_name
        self._debug( 'Open json_file : %s' %(json_file))

        if os.path.isfile( json_file ):
            self._debug( 'File (%s) exists' %(json_file))
        else:
            self._debug( 'File (%s) does NOT exists' %(json_file))
            self._error( 'File (%s) does NOT exists' %(json_file))
            return None

        json_data = json.loads( open( json_file ).read() )
        # pprint ( json_data )
        return json_data


    def load_quote(self ):
        json_file = self.priv_dir+'/quote.json'
        json_data = self._load_json( json_file )
        return json_data

    def load_detailed_quote(self):
        json_file = self.priv_dir+'/quote_detailed.json'
        json_data = self._load_json( json_file )
        return json_data


    ###################### Parsers ######################################
    # intended to be used with downloads. ie. as soon as you download parse and save it
    # optionally delete raw file.
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
    def __parse_alphavantage( self, input_raw_file_name, output_json_file_name ):
        # Takes in the raw file, and processes it to standard format
        self._debug( 'Parsing file %s' %(input_raw_file_name) )
        data_raw = json.loads( open(input_raw_file_name).read(), object_pairs_hook=OrderedDict )

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
