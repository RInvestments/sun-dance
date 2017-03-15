""" Processor for HKEX profile
        Sample : http://www.hkex.com.hk/eng/invest/company/profile_page_e.asp?WidCoID=0341

        This class will provide function a) download from url, b) load from file if exist
        c) process the dump d) many many getter functions

"""
import sys
import os.path
import urllib2
import time
import code
from bs4 import BeautifulSoup
import pickle

import collections
import json
from pprint import pprint
def Tree():
    return collections.defaultdict(Tree)

import TerminalColors
tcol = TerminalColors.bcolors()

class SourceHKEXProfile:
    def _printer( self, txt ):
        print tcol.OKBLUE, 'SourceHKEXProfile :', tcol.ENDC, txt

    def _debug( self, txt, lvl=0 ):
        """ """
        to_print = []
        if lvl in to_print:
            print tcol.OKBLUE, 'SourceWSJ(Debug=%2d) :' %(lvl), tcol.ENDC, txt

    def _error( self, txt ):
        """ """
        print tcol.FAIL, 'SourceWSJ(Error) :', tcol.ENDC, txt

    def _report_time( self, txt ):
        print tcol.OKBLUE, 'SourceHKEXProfile(time) :', tcol.ENDC, txt


    def __init__(self, ticker, stock_prefix):
        """ ticker : Stock ticker eg. 2333.HK
        stock_prefix : Storage directory eg. eq_db/data_2016_Dec_09/0175.HK/
        """

        self.ticker = ticker
        self.stock_prefix = stock_prefix
        self.priv_dir = self.stock_prefix + '/hkex_profile/'
        self.raw_html_str = None

        self._debug( 'setting ticker : '+ ticker )
        self._debug( 'setting stock_prefix : '+ stock_prefix )
        self._debug( 'setting priv_dir : '+ self.priv_dir )

    def download_url(self, skip_if_exist=True):
        """ Having known the ticker and stock_prefix, download the files into the folder """
        # mkdir a folder within the stock_prefix (if not exits)

        if not os.path.exists(self.priv_dir):
            os.makedirs( self.priv_dir )

        #if file exist skip
        if skip_if_exist and os.path.isfile( self.priv_dir+'/profile_page_e.html' ):
            self._debug( "Raw html Exists...SKIP" )
            return True

        # Setup the url
        url = 'http://www.hkex.com.hk/eng/invest/company/profile_page_e.asp?WidCoID='+self.ticker[0:4]

        # download and write file
        startTime = time.time()
        self._debug( 'Download : '+url )
        status = self._download_and_save( url, self.priv_dir+'/profile_page_e.html')
        self._report_time( 'Downloaded in %2.4f sec' %(time.time()-startTime) )
        return status


    def _load_raw_file(self):
        """ Load the file. This file is assumed to already exist in priv_dir
                Returns true if the file was loaded successfully. False otherwise

        """

        raw_fname = self.priv_dir+'/profile_page_e.html' #raw info for this stock
        if os.path.exists( raw_fname ):
            self._debug( 'file exists and loaded : '+raw_fname )
            self.raw_html_str = open( raw_fname, 'r' ).read()
            self._debug( 'Loaded into self.raw_html_str' )
            return True
        else:
            self._printer( 'raw file does not exists : '+raw_fname)
            return False

    def parse(self, delete_raw=False):
        """ Parse the raw string with BeautifulSoup
                This function will look for variable `self.raw_html_str` which
                is the raw html string loaded by the load_file function. This is
                set to None in constructor and set to a valid string (?) in self.load_file()
        """

        if self.raw_html_str is None:
            self._load_raw_file()
            # self._printer( 'self.raw_html_str is None. You should call the function load_file() \
            # before calling the parse() function' )
            # return False

        startTime = time.time()
        soup = BeautifulSoup(str(self.raw_html_str), 'lxml')
        table = soup.find_all('table' )#, {"border" : '0', "width" : '98%'} )
        #all_tr = table.find_all( 'tr' )
        self._debug( '# of tables : '+str(len(table)) )
        # assert len(table) == 7
        if len(table) != 7:
            self._error( '# of tables not 7, corrpt ')
            return False

        findata_tree = self._process_table_financial_info( table[5] )
        # print self.ticker, '-', data_dict['Industry Classification']

        dividend_tree = self._process_dividents_table( table[6] )


        # Save obj
        # pickle_fname = self.priv_dir+'/data_dict.pk1'
        # self._debug( 'Write pickle file : '+pickle_fname )
        # self._save_obj( data_dict, pickle_fname )

        # Save json
        json_string = json.dumps(findata_tree, indent=4)
        self._debug( 'findata_tree\n'+ json_string, lvl=1 )
        json_fname = self.priv_dir+'/hkex_profile.json'
        json.dump( findata_tree, open(json_fname, 'w') )
        self._debug( "File Written : "+json_fname)

        json_string = json.dumps(dividend_tree, indent=4)
        self._debug( 'dividend_tree\n'+ json_string, lvl=1 )
        json_fname = self.priv_dir+'/dividends.json'
        json.dump( dividend_tree, open(json_fname, 'w') )
        self._debug( "File Written : "+json_fname)


        # Delete raw html file (~55Kb each)
        if delete_raw == True:
            self._debug( 'rm '+self.priv_dir+'/profile_page_e.html' )
            os.remove( self.priv_dir+'/profile_page_e.html' )

        self._report_time( 'Parsed in %2.4f sec' %(time.time()-startTime) )


        return True

    def load_pickle(self):
        """ Loads the pickle file which should exists. Pickle file is created in
        call to function parse(). """

        # Check if pickle file exits
        pickle_fname = self.priv_dir+'/data_dict.pk1'
        if os.path.exists( pickle_fname ):
            self._debug( 'Exists pickle file : '+pickle_fname )
            self.data_dict = self._load_obj( pickle_fname )
        else:
            self._debug( 'Missing pickle file : '+pickle_fname )



    def _process_table_financial_info( self, table ):
        """ Given table 5 (table containing Principal Activities, Chairman etc etc), process this table and make a
        dictionary out of it.

        {'Authorised Shares': '4,000,000,000',
         'Board Lot': '2000',
         'Chairman': 'Ngai Chun Hung',
         'Company/Securities Name': 'Vantage International (Holdings) Ltd.',
         'Earnings per Share': 'HKD 0.4423',
         'Financial Year End Date': '31/3/2016',
         'Industry Classification': 'Properties & Construction - Construction - Building Construction (HSIC*)',
         'Issued Shares(Click here for important notes)': '1,760,524,400(as at 2/12/2016)',
         'Last Updated': '10/12/2016',
         'Listing Category': 'Primary Listing',
         'Listing Date': '8/9/2000',
         'Market Capitalisation': 'HKD 2,024,603,060',
         'Net Asset Value': 'HKD2,765,616,000',
         'Net Profit (Loss)': 'HKD772,483,000',
         'Par Value': 'HKD0.0250',
         'Place Incorporated': 'Bermuda',
         'Principal Activities': 'Provision of construction, civil engineering, maintenance and other contract works in public and private sectors in Hong Kong, property investment and development.',
         'Principal Office': 'No 155 Waterloo RoadKowloon TongKowloon Hong Kong',
         'Registrar': 'Tricor Tengis Ltd.',
         'Trading Currency': 'HKD'}
        """


        tab_soup = BeautifulSoup(str(table), 'lxml')
        all_tr = tab_soup.find_all( 'tr' )
        data_dict = {}
        data_tree = Tree()
        for i,tr in enumerate(all_tr):
            all_td = tr.find_all('td')
            if len(all_td) == 2:
                key = all_td[0].get_text().encode('utf-8').replace('\n', '').replace('\r', '').replace('\t', '').replace(':', '').strip()
                value = all_td[1].get_text().encode('utf-8').replace('\n', '').replace(':', '').replace('\xc2\xa0','').strip()
                data_dict[key] = value
                data_tree[key] = value
                # print i,')',key, ":", value

        # json_string = json.dumps(data_tree, indent=4)
        # print json_string

        return data_tree


    def _process_dividents_table( self, table ):
        """
        {
        "03/08/2016": {
            "Financial year end": "31/12/2016",
            "Ex-date": "11/08/2016",
            "B/C date": "",
            "Details": "2nd Int Div USD 0.10(approx. HKD 0.775761)(with scrip, GBP or HKD, orcombination of these currencies option)(Record date: 2016/08/12)",
            "Payment date*": "28/09/2016"
        },
        .
        .
        """
        all_tr = table.find_all( 'tr' )
        header = []
        tree = Tree()

        for tr in all_tr:
            all_td = tr.find_all('td')
            if len(all_td) == 6:

                if len(header) == 0:
                    # print tcol.BOLD,
                    for td in all_td:
                        # print td.text.strip()
                        header.append(td.text.strip())
                    # print tcol.ENDC
                    continue


                tree[all_td[0].text.strip()][header[1]] = all_td[1].text.strip()
                tree[all_td[0].text.strip()][header[2]] = all_td[2].text.strip()
                tree[all_td[0].text.strip()][header[3]] = all_td[3].text.strip()
                tree[all_td[0].text.strip()][header[4]] = all_td[4].text.strip()
                tree[all_td[0].text.strip()][header[5]] = all_td[5].text.strip()

        # json_string = json.dumps(tree, indent=4)
        # print json_string

        return tree

    def _download_and_save( self, url, fname ):
        if url is None:
            self._debug( 'URL is None, Skipping...' )
            return False
        self._debug( 'download :'+ url )
        self._debug( 'write to : '+ fname )
        hkex_html = urllib2.urlopen( url ).read() #if timeout happens rerun the script should be able to recover
        #TODO: Handle timeou
        with open(fname, "w") as handle:
            handle.write( hkex_html )
        return True


    ## Will be deprecated soon. Use json
    def _save_obj( self, obj, name ):
        """ Loads a data_dict from pickle """
        with open( name , 'wb') as f:
            pickle.dump( obj, f, pickle.HIGHEST_PROTOCOL )

    ## Will be deprecated soon. use json
    def _load_obj( self, name ):
        with open( name, 'rb' ) as f:
            return pickle.load(f)



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

    def load_hkex_profile( self ):
        json_file = self.priv_dir+'/hkex_profile.json'
        json_data = self._load_json( json_file )
        return json_data


    def load_dividends_data( self ):
        json_file = self.priv_dir+'/dividends.json'
        json_data = self._load_json( json_file )
        return json_data
