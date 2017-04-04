""" Processor for WSJ

        This class will provide function a) download from url, b) load from file if exist
        c) process the dump d) many many getter functions

"""
import sys
import os.path
import urllib2
import time
import code
import string
import glob

from bs4 import BeautifulSoup
import pickle

import collections
import json
from pprint import pprint
def Tree():
    return collections.defaultdict(Tree)

import TerminalColors
tcol = TerminalColors.bcolors()
tcolor = tcol


class SourceWSJ:
    def _printer( self, txt ):
        """ """
        print tcol.OKBLUE, 'SourceWSJ :', tcol.ENDC, txt

    def _error( self, txt ):
        """ """
        print tcol.FAIL, 'SourceWSJ(Error) :', tcol.ENDC, txt

    def _debug( self, txt, lvl=0 ):
        """ """
        to_print = self.verbosity
        if lvl in to_print:
            print tcol.OKBLUE, 'SourceWSJ(Debug=%2d) :' %(lvl), tcol.ENDC, txt

    def _report_time( self, txt ):
        """ """
        print tcol.OKBLUE, 'SourceWSJ(time) :', tcol.ENDC, txt

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

    def _load_raw_html(self, raw_fname):
        """ Given a file name (html), loads the file and returns the html string. Returns None if file does not exist """
        if os.path.exists( raw_fname ):
            self._debug( 'file exists and loaded : '+raw_fname )
            raw_html_str = open( raw_fname, 'r' ).read()
            self._debug( 'Loaded into `raw_html_str`' )
            return raw_html_str
        else:
            self._error( 'raw file does not exists : '+raw_fname)
            return None

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
        self.priv_dir = stock_prefix + '/wsj/'
        self.raw_html_str = None



        self._debug( 'setting ticker : '+ ticker )
        self._debug( 'setting stock_prefix : '+ stock_prefix )
        self._debug( 'setting priv_dir : '+ self.priv_dir )

    def download_url(self, skip_if_exist=True):
        """ Having known the ticker and stock_prefix, download the files into the folder """
        # mkdir a folder within the stock_prefix (if not exits)
        if not os.path.exists(self.priv_dir):
            os.makedirs( self.priv_dir )

        # #TODO: Instead of just checking exisitence of overview, put this code in _download_and_save() to check for exisitence of each file
        # if skip_if_exist and os.path.isfile( self.priv_dir+'/overview.html' ):
        #     self._debug( "Raw html Exists:" +self.priv_dir+'/overview.html' + "...SKIP" )
        #     return True

        # Setup the url(s).
        wsg_ticker = self.ticker[0:4]#ticker in WSG format
        url_financials = 'http://quotes.wsj.com/HK/XHKG/%s/financials' %(wsg_ticker)
        url_wsj_profile = 'http://quotes.wsj.com/HK/XHKG/%s/company-people' %(wsg_ticker)

        url_income_statement = 'http://quotes.wsj.com/HK/XHKG/%s/financials/annual/income-statement' %(wsg_ticker)
        url_balance_sheet = 'http://quotes.wsj.com/HK/XHKG/%s/financials/annual/balance-sheet' %(wsg_ticker)
        url_cash_flow_statement = 'http://quotes.wsj.com/HK/XHKG/%s/financials/annual/cash-flow' %(wsg_ticker)

        url_income_statement_q = 'http://quotes.wsj.com/HK/XHKG/%s/financials/quarter/income-statement' %(wsg_ticker)
        url_balance_sheet_q = 'http://quotes.wsj.com/HK/XHKG/%s/financials/quarter/balance-sheet' %(wsg_ticker)
        url_cash_flow_statement_q = 'http://quotes.wsj.com/HK/XHKG/%s/financials/quarter/cash-flow' %(wsg_ticker)




        # retrive file and write file
        startTime = time.time()
        if skip_if_exist and os.path.exists(self.priv_dir+'financials.html'):
            self._debug( 'Already exists file : %s .... SKIPPING' %(self.priv_dir+'financials.html') )
        else:
            self._download_and_save( url_financials, self.priv_dir+'financials.html')

        if skip_if_exist and os.path.exists(self.priv_dir+'wsj_profile.html'):
            self._debug( 'Already exists file : %s .... SKIPPING' %(self.priv_dir+'wsj_profile.html') )
        else:
            self._download_and_save( url_wsj_profile, self.priv_dir+'wsj_profile.html')

        if skip_if_exist and os.path.exists(self.priv_dir+'income_statement.html') and os.path.exists(self.priv_dir+'income_statement_q.html'):
            self._debug( 'Already exists file : %s .... SKIPPING' %(self.priv_dir+'income_statement.html') )
        else:
            self._download_and_save( url_income_statement, self.priv_dir+'income_statement.html')
            self._download_and_save( url_income_statement_q, self.priv_dir+'income_statement_q.html')

        if skip_if_exist and os.path.exists(self.priv_dir+'balance_sheet.html') and os.path.exists(self.priv_dir+'balance_sheet_q.html'):
            self._debug( 'Already exists file : %s .... SKIPPING' %(self.priv_dir+'balance_sheet.html') )
        else:
            self._download_and_save( url_balance_sheet, self.priv_dir+'balance_sheet.html')
            self._download_and_save( url_balance_sheet_q, self.priv_dir+'balance_sheet_q.html')

        if skip_if_exist and os.path.exists(self.priv_dir+'cash_flow_statement.html') and os.path.exists(self.priv_dir+'cash_flow_statement_q.html'):
            self._debug( 'Already exists file : %s .... SKIPPING' %(self.priv_dir+'cash_flow_statement.html') )
        else:
            self._download_and_save( url_cash_flow_statement, self.priv_dir+'cash_flow_statement.html')
            self._download_and_save( url_cash_flow_statement_q, self.priv_dir+'cash_flow_statement_q.html')


        self._report_time( 'Downloaded in %2.4f sec' %(time.time()-startTime) )


    def parse(self, delete_raw=False):
        #TODO
        # Add a function to check if the data even exists
        self.parse_financial_statements(delete_raw=delete_raw)
        self.parse_profile(delete_raw=delete_raw)
        self.parse_financials(delete_raw=delete_raw)



    ## Parses the .html of financial statements to .json
    def parse_financial_statements(self, delete_raw=False):
        """ Parse the downloaded files and save the data as pickle"""
        A = {}
        A['income_statement'] = self.priv_dir+'income_statement.html'
        A['income_statement_q'] = self.priv_dir+'income_statement_q.html'
        A['balance_sheet'] = self.priv_dir+'balance_sheet.html'
        A['balance_sheet_q'] = self.priv_dir+'balance_sheet_q.html'
        A['cash_flow_statement'] = self.priv_dir+'cash_flow_statement.html'
        A['cash_flow_statement_q'] = self.priv_dir+'cash_flow_statement_q.html'

        F = {}
        F['financials'] = self.priv_dir+'financials.'
        F['income_statement'] = self.priv_dir+'income_statement.a.'
        F['income_statement_q'] = self.priv_dir+'income_statement.q.'
        F['balance_sheet'] = self.priv_dir+'balance_sheet.a.'
        F['balance_sheet_q'] = self.priv_dir+'balance_sheet.q.'
        F['cash_flow_statement'] = self.priv_dir+'cash_flow_statement.a.'
        F['cash_flow_statement_q'] = self.priv_dir+'cash_flow_statement.q.'


        startTime = time.time()
        status = self._parse_income_statement( A['income_statement_q'], F['income_statement_q'] )
        status = self._parse_income_statement( A['income_statement'], F['income_statement'] )

        status = self._parse_balance_sheet( A['balance_sheet_q'], F['balance_sheet_q'] )
        status = self._parse_balance_sheet( A['balance_sheet'], F['balance_sheet'] )

        status = self._parse_cash_flow_statement( A['cash_flow_statement_q'], F['cash_flow_statement_q'] )
        status = self._parse_cash_flow_statement( A['cash_flow_statement'], F['cash_flow_statement'] )
        self._report_time( 'Parsing done in %4.2fs' %(time.time()-startTime) )


        # Delete raw html file (~55Kb each)
        if delete_raw == True:
            for ulr in A:
                self._debug( 'rm '+A[ulr] )
                os.remove( A[ulr] )


    ## Parses the company-people html page
    def parse_profile(self, delete_raw=False):
        raw_html = self._load_raw_html( self.priv_dir+'wsj_profile.html' )
        if raw_html is None:
            return

        soup = BeautifulSoup( str(raw_html), 'lxml' )
        wsj_profile_tree = Tree()

        # Company Info/Contact Address
        dat_company_info = soup.find_all( 'div', attrs={'data-module-id': 4 } )
        if len(dat_company_info) == 0:
            self._error( 'data module 4 not found in wsj_profile.html')
            return False

        contact_addr = dat_company_info[0].find_all( 'div', class_='cr_profile_contact')
        out_address = []
        for ln in contact_addr[0].find_all('span'):
            # print ln.string
            if ln.string is not None:
                out_address.append( ln.string.strip() )
        out_address = ','.join(out_address)
        wsj_profile_tree['Contact Address'] = out_address

        # Company Info/Cr overview data
        dat_overview = dat_company_info[0].find_all( 'div', class_='cr_overview_data' )
        all_data_lbl = dat_overview[0].find_all( 'span', class_='data_lbl' )
        all_data_data = dat_overview[0].find_all( 'span', class_='data_data' )
        for i in range( len(all_data_lbl) ):
            # print all_data_lbl[i].text, ':', all_data_data[i].text
            wsj_profile_tree['Company Info'][all_data_lbl[i].text.strip()] = all_data_data[i].text.strip()


        # Description
        dat_description = soup.find( 'div', attrs={'data-module-id': 5 } )
        if dat_description is None:
            self._error( 'data module 5 not found in wsj_profile.html')
            return False

        if dat_description.find( 'p', class_='txtBody') is not None:
            out_description = dat_description.find( 'p', class_='txtBody').text
        else:
            out_description = 'N/A'
        wsj_profile_tree['Description'] = out_description.strip()
        # print out_description


        self._debug( 'overview_json_string\n'+ json.dumps( wsj_profile_tree, indent=4 ), lvl=1 )
        json_fname = self.priv_dir+'wsj_profile.json'
        json.dump( wsj_profile_tree, open(json_fname, 'w') )
        self._debug( "File Written : "+json_fname)


        # Ownership
        # print '---'
        dat_ownership = soup.find(  'div', attrs={'data-module-id': 9 } )
        tables = dat_ownership.find_all( 'div', class_='scrollBox' )
        if len(tables) != 2:
            self._error( 'parse_profile : No ownership tables. Not writing ')
            return False
        mutual_fund_owners = tables[0]
        institutional_investors = tables[1]
        tree_mutual_fund_owners = self._parse_ownership_table( mutual_fund_owners )
        tree_institutional_investors = self._parse_ownership_table( institutional_investors )
        mutual_fund_owners_json_string = json.dumps( tree_mutual_fund_owners, indent=4 )
        institutional_investors_json_string = json.dumps( tree_institutional_investors, indent=4 )
        self._debug( 'mutual_fund_owners_json_string\n'+mutual_fund_owners_json_string, lvl=1 )
        self._debug( 'institutional_investors_json_string\n'+institutional_investors_json_string, lvl=1 )

        json_fname = self.priv_dir+'mutual_fund_owners.json'
        json.dump( tree_mutual_fund_owners, open(json_fname, 'w') )
        self._debug( "File Written : "+json_fname)

        json_fname = self.priv_dir+'institutional_investors.json'
        json.dump( tree_institutional_investors, open(json_fname, 'w') )
        self._debug( "File Written : "+json_fname)


        # Delete raw html file (~55Kb each)
        if delete_raw == True:
            self._debug( 'rm '+self.priv_dir+'wsj_profile.html' )
            self._rm_if_exists( self.priv_dir+'wsj_profile.html' )


    def parse_financials(self, delete_raw=False ):
        """ Parses the raw string and returns json encoded string"""
        raw_html = self._load_raw_html( self.priv_dir+'financials.html' )
        if raw_html is None:
            return

        soup = BeautifulSoup(str(raw_html), 'lxml')
        tree = Tree()

        earnings_estimates = soup.find_all( attrs={'data-module-id': 4 } ) # Earning and Estimates
        if len(earnings_estimates) != 1:
            self._error( 'data module 4 not found in parse_financials')
            return False
        lbl = earnings_estimates[0].find_all( 'span', class_='data_lbl' )
        dat = earnings_estimates[0].find_all( 'span', class_='data_data' )
        # print tcolor.HEADER, 'Earning and Estimates', tcolor.ENDC
        for i in range(len(lbl)):
            # print tcolor.BOLD, lbl[i].get_text(), tcolor.ENDC, dat[i].get_text()
            tree['Earning and Estimates'][lbl[i].get_text().strip()] = dat[i].get_text().strip()


        per_share_data = soup.find_all( attrs={'data-module-id': 5 } )[0]
        lbl = per_share_data.find_all( 'span', class_='data_lbl' )
        dat = per_share_data.find_all( 'span', class_='data_data' )
        # print tcolor.HEADER, 'Per Share Data', tcolor.ENDC
        for i in range(len(lbl)):
            # print tcolor.BOLD, lbl[i].get_text(), tcolor.ENDC, dat[i].get_text()
            tree['Per Share Data'][lbl[i].get_text()] = dat[i].get_text()



        ratios_n_margin = soup.find_all( attrs={'data-module-id': 7 } )[0]
        all_tr = ratios_n_margin.find_all( 'tr' )
        # print tcolor.HEADER, 'Ratios and Margins', tcolor.ENDC
        for tr in all_tr:
            lbl = tr.find( 'span', class_='data_lbl' ).text.strip()
            data = tr.find( 'span', class_='data_data' ).text.strip()
            # print tcolor.BOLD, lbl, tcolor.ENDC, data
            tree[ 'Ratios and Margins'][lbl] = data


        json_string = json.dumps(tree, indent=4)
        # print json_string
        json_fname = self.priv_dir+'/financials.json'
        json.dump( tree, open(json_fname, 'w') )
        self._debug( "File Written : "+json_fname)


        # Delete raw html file (~55Kb each)
        if delete_raw == True:
            self._debug( 'rm '+self.priv_dir+'financials.html' )
            self._rm_if_exists( self.priv_dir+'financials.html' )



    ## Parse either of tables 'Mutual Funds that own 0001' or 'Institutionas that own 0001'.
    ## Returns the tree.
    def _parse_ownership_table( self, table ):
        tree = Tree()
        all_tr = table.find_all( 'tr' )
        for tr in all_tr:
            all_td = tr.find_all( 'td' )
            tree[all_td[0].text]['Shares Held'] = all_td[1].text
            tree[all_td[0].text]['Percent Shares Out'] = all_td[2].text
            tree[all_td[0].text]['Change In Shares'] = all_td[3].text
            tree[all_td[0].text]['Percent of Assets'] = all_td[4].text
            tree[all_td[0].text]['As of Date'] = all_td[5].text
            # for td in all_td:
            #     print td.text,
            # print ''
        return tree





    def _parse_cash_flow_statement( self, raw_html_filename, out_json_filename ):
        """ Parses the cash-flow statement """
        raw_html = self._load_raw_html( raw_html_filename )
        if raw_html is None:
            return

        soup = BeautifulSoup(str(raw_html), 'lxml')

        dat_mod_3 = soup.find_all( 'div', attrs={'data-module-id': 3 } )
        if len(dat_mod_3) < 1:
            self._error( '_parse_cash_flow_statement dat module 3 does not exist')
            return False

        cash_flow_statement = dat_mod_3[0]
        tmp = cash_flow_statement.find_all( 'table', class_='cr_dataTable')
        if len(tmp) < 1:
            self._error( '_parse_cash_flow_statement doesnot seem to contain data table')
            return False
        operating_activities = tmp[0]
        investing_activities = tmp[1]
        financing_activities = tmp[2]

        self._debug( '----------Operating----------' )
        forest_operating = self.__parse_crTable(operating_activities)

        self._debug( '----------Investing----------' )
        forest_investing = self.__parse_crTable(investing_activities)

        self._debug( '----------Financing----------' )
        forest_financing = self.__parse_crTable(financing_activities)

        #Write json
        for u in range(len(forest_operating)):
            # path-eg : path/cash_flow_statement.q.operating.2015.json
            json_fname = out_json_filename+'operating.'+forest_operating[u]['_HEADER_']+'.json'
            json.dump( forest_operating[u], open(json_fname, 'w') )
            self._debug( "File Written : "+json_fname)

            # path-eg : path/cash_flow_statement.q.operating.2015.json
            json_fname = out_json_filename+'investing.'+forest_investing[u]['_HEADER_']+'.json'
            json.dump( forest_investing[u], open(json_fname, 'w') )
            self._debug( "File Written : "+json_fname)

            # path-eg : path/cash_flow_statement.q.operating.2015.json
            json_fname = out_json_filename+'financing.'+forest_financing[u]['_HEADER_']+'.json'
            json.dump( forest_financing[u], open(json_fname, 'w') )
            self._debug( "File Written : "+json_fname)

        return True



    def _parse_balance_sheet(self, raw_html_filename, out_json_filename):
        """ Parse the balance sheet. Has 2 parts viz. Assets, Liabilities """
        raw_html_str = self._load_raw_html( raw_html_filename )
        if raw_html_str is None:
            return

        soup = BeautifulSoup(str(raw_html_str), 'lxml')

        balance_sheet = soup.find_all( 'div', attrs={'data-module-id': 3 } )[0]
        tmp = balance_sheet.find_all( 'table', class_='cr_dataTable')
        if len(tmp) < 1:
            self._error( '_parse_balance_sheet doesnot seem to contain data table')
            return False
        assets_table = tmp[0]
        liabilities_table = tmp[1]
        self._debug( '----------ASSETS----------' )
        forest_assets = self.__parse_crTable(assets_table)

        self._debug( '------LIABILITIES---------' )
        forest_liabilities = self.__parse_crTable(liabilities_table)

        # Write to file (JSON)
        for u in range(len(forest_assets)):
            # json_string = json.dumps(forest_assets[u], indent=4)
            # eg: path/balance_sheet.q.assets.2015.json
            json_fname = out_json_filename+'assets.'+forest_assets[u]['_HEADER_']+'.json'
            json.dump( forest_assets[u], open(json_fname, 'w') )
            self._debug( "File Written : "+json_fname)

            # eg: path/balance_sheet.q.assets.2015.json
            json_fname = out_json_filename+'liabilities.'+forest_liabilities[u]['_HEADER_']+'.json'
            json.dump( forest_liabilities[u], open(json_fname, 'w') )
            self._debug( "File Written : "+json_fname)

        return True





    def _parse_income_statement(self, raw_html_filename, out_json_filename ):
        """ Parse the income-statement. Return json for each of the seen income statement """
        raw_html = self._load_raw_html( raw_html_filename )
        if raw_html is None:
            return
        soup = BeautifulSoup(str(raw_html), 'lxml')

        income_statement = soup.find_all( attrs={'data-module-id': 3 } )[0]
        data_table = income_statement.find_all( 'table', class_='cr_dataTable' )
        if len(data_table) < 1:
            self._error( '_parse_income_statement doesnot seem to contain data table')
            return False

        forest = self.__parse_crTable(data_table[0])


        for u in range(len(forest)):
            json_string = json.dumps(forest[u], indent=4)
            json_fname = out_json_filename+forest[u]['_HEADER_']+'.json'
            json.dump( forest[u], open(json_fname, 'w') )
            self._debug( "File Written : "+json_fname)


        return True



    ## Parses the data_table and returns the heirarchical object tree. Will
    ## return multiple trees, equal to number of headers. Each of the return
    ## object is a Tree(). Can be indexed as arrays
    def __parse_crTable( self, data_table ):

        forest = []

        #HEADER
        header = data_table.find_all( 'thead' )[0].find_all('th')
        for u in range(1,len(header)-1):
            self._debug('HEADER %d %s' %(u, header[u].string)) #1,2,3,4,5 are valid value

            tr = Tree()
            tr['_HEADER_'] = header[u].string
            forest.append(tr)

        #Other data
        all_tr = BeautifulSoup(str(data_table), 'lxml').find_all( 'tbody' )[0].find_all('tr', recursive=False )
        for u in range(0,len(all_tr)):
            all_td = all_tr[u].find_all( 'td' )
            tag = all_td[0].string.strip()
            tag_class = all_td[0].get('class')[0]
            #TODO: number of data cols can be determinted based pm number of headers
            data_1 = all_td[1].string
            data_2 = all_td[2].string
            data_3 = all_td[3].string
            data_4 = all_td[4].string
            if 'indent2' in tag_class:
                tab = '<  >'+'<  >'
                for h in range(len(forest)):
                    forest[h][parent_l0][parent_l1][tag]['_E3M5_'] = all_td[h+1].string
            elif 'indent' in tag_class:
                tab = '<  >'
                parent_l1 = tag
                for h in range(len(forest)):
                    forest[h][parent_l0][tag]['_E3M5_'] = all_td[h+1].string

            else:
                tab = '' #parent ds
                parent_l0 = tag
                for h in range(len(forest)):
                    forest[h][tag]['_E3M5_'] = all_td[h+1].string

            if tab is not '': #child
                self._debug( '%02d |%s| |%s| %s' %(u, tab, tag, data_1), lvl=1 )#,data_2,data_3,data_4
            else: #base-data
                self._debug( '%02d |%s| %s' %(u, tag, data_1), lvl=1 )#,data_2,data_3,data_4


        return forest


    def __parse_crTable_bak( self, data_table ):
        #HEADER
        header = data_table.find_all( 'thead' )[0].find_all('th')
        for u in range(1,len(header)-1):
            print u, header[u].string #1,2,3,4,5 are valid value

        #Other data
        all_tr = BeautifulSoup(str(data_table), 'lxml').find_all( 'tbody' )[0].find_all('tr', recursive=False )
        for u in range(0,len(all_tr)):
            all_td = all_tr[u].find_all( 'td' )
            tag = all_td[0].string.strip()
            tag_class = all_td[0].get('class')[0]
            #TODO: number of data cols can be determinted based pm number of headers
            data_1 = all_td[1].string
            data_2 = all_td[2].string
            data_3 = all_td[3].string
            data_4 = all_td[4].string
            if 'indent2' in tag_class:
                tab = '<  >'+'<  >'
            elif 'indent' in tag_class:
                tab = '<  >'
            else:
                tab = ''

            if tab is not '':
                print '%02d |%s| |%s|' %(u, tab, tag), data_1#,data_2,data_3,data_4
            else:
                print '%02d |%s|' %(u, tag), data_1#,data_2,data_3,data_4



    ################ list (ls) available statements ############
    ## Will return available tags
    # period         : 'a' or 'q'
    # statement_name : 'income_statement' or 'balance_sheet' or 'cash_flow_statement'
    # sub_statement  :
    #        if 'income_statement' then None
    #        if 'balance_sheet' then 'assets' or 'liabilities'
    #        if 'cash_flow_statement' then 'operating' or 'investing' or 'financing'
    #
    # Note: sub_statement = None will return all sub statements
    # Note: Currently the check is not in place. PLease excersice care.
    #TODO: Implement checking of arguments
    def ls(self, period, statement_name, sub_statement=None):
        if sub_statement is None:
            pattern = '%s.%s.*.json' %(statement_name,period)
        else:
            pattern = '%s.%s.%s*.json' %(statement_name,period, sub_statement)
        self._debug( 'ls %s' %(pattern))
        self._debug( 'ls %s/%s' %(self.priv_dir,pattern), lvl=2 )
        ll = glob.glob( self.priv_dir+'/%s' %(pattern) )
        tags_list = []
        for l in ll:
            # get the last with split(/) and then split('.') and then join 1 to -1
            tags_list.append(  '.'.join( l.split('/')[-1].split('.')[1:-1] )  )
        return tags_list


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

    ##eg-tag : a.2015
    ##eg-tag : q.30-Jun-2014
    def load_json_income_statement( self, tag ):
        json_file = self.priv_dir+'/income_statement.'+tag+'.json'
        json_data = self._load_json( json_file )
        return json_data

    ##eg-tag : a.assets.2015
    ##eg-tag : a.liabilities.2015
    ##eg-tag : q.assets.30-Jun-2014
    ##eg-tag : q.liabilities.30-Jun-2014
    def load_json_balance_sheet( self, tag ):
        json_file = self.priv_dir+'/balance_sheet.'+tag+'.json'
        json_data = self._load_json( json_file )
        return json_data

    ##eg-tag : a.operating.2015
    ##eg-tag : a.investing.2015
    ##eg-tag : a.financing.2015
    ##eg-tag : q.operating.30-Jun-2014
    ##eg-tag : q.investing.30-Jun-2014
    ##eg-tag : q.financing.30-Jun-2014
    def load_json_cash_flow_statement( self, tag ):
        json_file = self.priv_dir+'/cash_flow_statement.'+tag+'.json'
        json_data = self._load_json( json_file )
        return json_data


    def load_json_profile( self ):
        json_file = self.priv_dir+'/wsj_profile.json'
        json_data = self._load_json( json_file )
        return json_data

    def load_mututal_fund_owners( self ):
        json_file = self.priv_dir+'/mutual_fund_owners.json'
        json_data = self._load_json( json_file )
        return json_data

    def load_institutional_investors( self ):
        json_file = self.priv_dir+'/institutional_investors.json'
        json_data = self._load_json( json_file )
        return json_data


    def load_financials( self ):
        json_file = self.priv_dir+'/financials.json'
        json_data = self._load_json( json_file )
        return json_data
