import sys
import os.path
import urllib2
import time
import code
import string

import pickle
import json

import TerminalColors
tcol = TerminalColors.bcolors()

from yahoo_finance import Share
from yahoo_finance import YQLResponseMalformedError

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

    def download_quote( self ):
        """ Stores only price and volume at datastart to json"""
        if not os.path.exists(self.priv_dir):
            self._debug( 'Make directory : '+self.priv_dir)
            os.makedirs( self.priv_dir )

        startTime = time.time()

        self._debug( 'Query yahoo_finance for '+self.ticker )
        try:
            sh = Share( self.ticker ) #ensure ticker is in yahoo's format
            data_dict = {}

            data_dict['get_price'] = sh.get_open()
            data_dict['get_volume'] = sh.get_volume()

            out_json_filename = self.priv_dir + '/quote.json'
            self._debug( '\n'+ json.dumps( data_dict, indent=4 ) )
            json.dump( data_dict, open(out_json_filename, 'w') )
            self._debug( "File Written : "+out_json_filename)
            self._report_time( 'Downloaded in %2.4f sec' %(time.time()-startTime) )
        except YQLResponseMalformedError:
            self._error( 'YQLResponseMalformedError, not writing json' )


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
        self._debug( '\n'+ json.dumps( data_dict, indent=4 ) )
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
