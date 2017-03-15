
import sys
import os.path
import urllib2

from bs4 import BeautifulSoup
from yahoo_finance import Share

import pickle

def download_and_save( url, fname ):
    if url is None:
        print 'URL is None, Skipping...'
        return
    hkex_html = urllib2.urlopen( url ).read()
    with open(fname, "w") as handle:
        handle.write( hkex_html )


def save_obj( obj, name ):
    """ Loads a data_dict from pickle """
    with open( name , 'wb') as f:
        pickle.dump( obj, f, pickle.HIGHEST_PROTOCOL )


def load_obj( name ):
    with open( name, 'rb' ) as f:
        return pickle.load(f)


""" The .pk1 file contains :
{'Authorised Shares': '8,000,000,000\r\t\t\t\t\t\xc2\xa0',
 'Board Lot': '500\xc2\xa0',
 'Chairman': 'Li Ka Shing\xc2\xa0',
 'Company/Securities Name': 'CK Hutchison Holdings Ltd.',
 'Earnings per Share': 'HKD 36.907\xc2\xa0',
 'Financial Year End Date': '31/12/2015\xc2\xa0',
 'Industry Classification': 'Conglomerates - Conglomerates - Conglomerates (HSIC*)                  \xc2\xa0',
 'Issued Shares\r\t\t\t\t\t\t\t(Click here for important notes)': '3,859,678,500\xc2\xa0(as at 31/10/2016)\r\t\t\t\t\t\xc2\xa0',
 'Last Updated': '26/11/2016 \xc2\xa0',
 'Listing Category': 'Primary Listing \xc2\xa0',
 'Listing Date': '1/11/1972\xc2\xa0',
 'Market Capitalisation': 'HKD 367,055,425,350\r\xc2\xa0',
 'Net Asset Value': 'HKD\xc2\xa0428,588,000,000\xc2\xa0',
 'Net Profit (Loss)': 'HKD\xc2\xa0118,570,000,000\xc2\xa0',
 'Par Value': 'HKD\xc2\xa01.0000\r                  \t\xc2\xa0',
 'Place Incorporated': 'Cayman Islands \xc2\xa0',
 'Principal Activities': 'Property development and investment, hotel and serviced suite operation, property and project management, and investment in infrastructure businesses and securities, ownership and leasing of movable assets.\xc2\xa0',
 'Principal Office': "12/F, Cheung Kong Center2 Queen's Road CentralHong Kong\xc2\xa0",
 'Registrar': 'Computershare Hong Kong Investor Services Ltd.\xc2\xa0',
 'Trading Currency': 'HKD\xc2\xa0',
 'lot_size': 500,
 'ticker': u'0001.HK'}
"""


def process_hkex_list( html, download_profiles=False, force_download_profiles=False, process_hkex_html_profiles=False  ):
    """ html : html of the list
        download_profiles : If set to false will not download profiles. If set to True will download profiles if the profile do not exist in the folder 'equities_data/'
        force_download_profiles : If set to true will forcefully download the profiles and overwrite existing.
        process_hkex_html_profiles : if set to true will load the raw html file of the hkex profile. Extract all the cols of the table5 and save as an dictionary pickle

        USE EITHER OF THE FLAG. DO NOT USE BOTH TOGETHER

        #TODO : Have a check if both flags are used together
    """

    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', {"class" : 'table_grey_border'} )

    #print out.prettify()
    all_tr = table.find_all( 'tr' )

    # there are 7 td in each tr. 1st row, ie. header row contains 4
    # http://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty_pf.htm

    # rows to process
    si = len(all_tr) - 2
    for i in range(1,si):
        all_td = all_tr[i].find_all( 'td' )
        # print '----'
        ticker = all_td[0].string[1:]+'.HK'
        name = all_td[1].string
        hkex_profile_url = all_td[1].find('a')
        if hkex_profile_url is not None:
            hkex_profile_url = 'http://www.hkex.com.hk/eng/'+hkex_profile_url.get('href')[8:]

        lot_size = int(all_td[2].string.replace(',',''))

        # print 'Stock Ticker:', ticker
        print 'Name : ', name
        # print 'Lot size :', lot_size
        # print 'URL : ', hkex_profile_url
        # print 'flags : ', all_td[3].string, all_td[4].string, all_td[5].string, all_td[6].string




        # Download Additional Profile Info from HKEX
        if download_profiles == True:
            # check if exist file
            fname = 'equities_data/'+ticker
            if os.path.isfile(fname) == True:
                print 'Already exisits file ``', fname, '``. Not downloading'
            else:
                print 'File does not exits :``', fname, '``. Download....'
                download_and_save(hkex_profile_url, fname )

        if force_download_profiles == True:
            # Save HKEX url
            fname = 'equities_data/'+ticker
            download_and_save(hkex_profile_url, fname )
            print 'Force download : ``', fname,'``'



        # Get financial info table from hkex profile and dump as pickle
        if process_hkex_html_profiles == True:
            fname = 'equities_data/'+ticker
            if os.path.isfile(fname) == True:
                hkex_profile = open( fname, 'r' ).read()


                soup = BeautifulSoup(hkex_profile, 'lxml')
                table = soup.find_all('table' )#, {"border" : '0', "width" : '98%'} )
                #all_tr = table.find_all( 'tr' )

                data_dict = process_table_financial_info( table[5] )
                print name, '-', ticker, '-', data_dict['Industry Classification']


                # Add ticker, lot size, to data_dict
                data_dict['ticker'] = ticker
                data_dict['lot_size'] = lot_size

                # Data as pickle
                pickle_fname =  'equities_data/'+ticker+'.hkex_profile.pk1'
                print 'Saving pickle : ', pickle_fname
                save_obj(data_dict, pickle_fname)
            else:
                print 'Error : cannot load raw html for hkex profile : ', fname




        #load pickle
        pickle_fname =  'equities_data/'+ticker+'.hkex_profile.pk1'
        if os.path.isfile(pickle_fname) == True: #ensure the pickle file exists
            data_dict = load_obj( pickle_fname )
            print data_dict['ticker']
        else:
            print 'File does not exist : ', pickle_fname





def process_table_financial_info( table ):
    """ Given table 5 (table containing Principal Activities, Chairman etc etc), process this table and make a
    dictionary out of it.
    """

    tab_soup = BeautifulSoup(str(table), 'lxml')
    all_tr = tab_soup.find_all( 'tr' )
    data_dict = {}
    for i,tr in enumerate(all_tr):
        all_td = tr.find_all('td')
        if len(all_td) == 2:
            key = all_td[0].get_text().encode('utf-8').replace('\n', '').replace(':', '').strip()
            value = all_td[1].get_text().encode('utf-8').replace('\n', '').replace(':', '').strip()
            data_dict[key] = value
            #print i,')',key, value

    return data_dict


# Read from File
html = open( 'equities_data/eisdeqty.htm', 'r').read()


# Read URL
# html = urllib2.urlopen('http://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty.htm').read()  # List of securities


# process list
# process_hkex_list( html, download_profiles=True )
process_hkex_list( html, process_hkex_html_profiles=True )


# # process hkex-profilex
# hkex_profile = open( 'equities_data/0002.HK', 'r' ).read()
#
#
# soup = BeautifulSoup(hkex_profile, 'lxml')
# table = soup.find_all('table' )#, {"border" : '0', "width" : '98%'} )
# #all_tr = table.find_all( 'tr' )
#
# data_dict = process_table_financial_info( table[5] )
#process_table_divident_history( table[6] )


    # # Query yahoo_finance
    # quote = Share( ticker )
    # #print 'get_open ', quote.get_open()
    # price = quote.get_open()
    # if price is None:
    #     price = 0
    # else:
    #     price = float( price )
    # min_buy_hkd = price * lot_size
    # target_price = quote.get_one_yr_target_price()
    # # if target_price is None:
    # #     target_price = 0
    # # else:
    # #     target_price = float( target_price )
    # print min_buy_hkd,',', ticker,',', name, ',', target_price
