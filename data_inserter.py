""" Insert into mongodb
        This script can insert the parsed json data into a mongodb database.
        Make sure the mongodb database is correctly set and keys, unique indices
        correctly set. This script is intended to be run after `data_retriver.py`
        and `data_parser.py`.

        Author  : Manohar Kuse <mpkuse@connect.ust.hk>
                  Ayush Thakkar

        Created : 15 Mar, 2017
"""

import sys
import os.path
import urllib2
# import pprint
import os
import locale
import json
import collections
import socket
import pprint

import time
from datetime import datetime

import TerminalColors
tcol = TerminalColors.bcolors()

import argparse


from stockspotter.db.SourceHKEXProfile import SourceHKEXProfile
from stockspotter.db.SourceWSJ import SourceWSJ
from stockspotter.db.SourceReuters import SourceReuters
from stockspotter.lister.TickerLister import TickerLister

import urllib2
import uuid
import pymongo
import code



def __write( msg ):
    # print msg
    fp_logfile.write( msg +'\n')

def log_write( msg ):
    fp_logfile.write( msg+'\n' )

def log_server( msg ):
    if fp_logserver is not None:
        fp_logserver.sendall( '[%s:%6d:%s] ' %(__file__, os.getpid(), str(datetime.now())) + msg +'\n' )
    # fp_logfile.write( msg+'\n' )


def get_uuid( cur_dict ):
    od = collections.OrderedDict(sorted(cur_dict.items()))

    json_data_obj =  json.dumps(od)
    digest = uuid.uuid3(uuid.NAMESPACE_DNS, json_data_obj)
    return str(digest)

def log_debug( msg, lvl=1 ):
    if lvl in range( args.verbosity ):
        __write( '[DEBUG=%d]' %(lvl)+msg )

def add_to_db(cur_dict):
    global total_ok, per_ticker_ok, total_fail, per_ticker_fail

    cur_dict['id'] = get_uuid( cur_dict )
    json_cur_dict = json.dumps(cur_dict)







    ###########################
    #### MongoDB Insertion ####
    ###########################

    #code.interact(local=locals())

    try:
        cur_dict['last_modified'] = datetime.now()
        db.universalData.insert( cur_dict )
    except pymongo.errors.DuplicateKeyError, e:
        # Dup licate'
        log_debug( str(e), lvl=4 )
        log_debug( tcol.FAIL + 'DuplicateKeyError' + tcol.ENDC, lvl=3 )
        # uiii+= 1  #silently ignore this. may be report only in a verbose setting
        total_fail += 1
        per_ticker_fail += 1
        return False
    except Exception as e:
        #TODO catch the `Duplicate key insertion`. This denotes this data already exists
        log_debug( str(e)  )
        log_debug( tcol.FAIL+ 'MOngoDB insert failed'+ tcol.ENDC, lvl=3 )
        total_fail += 1
        per_ticker_fail += 1
        return False

    # del cur_dict
    total_ok += 1
    per_ticker_ok += 1
    return True


def solr_commit():
    req = urllib2.Request(url='http://localhost:8983/solr/universalData/update?commit=true')
    f = urllib2.urlopen(req)
    __write( f.read() )
    __write( "Solr Commit Done !!!" )


# h_string : '12 M' or '123 B' or '1.2 T'. Space is important
def human_readable_nums_to_int( h_string ):
    conv = {'M':1000000, 'B':1000000000, 'T':1000000000000}
    _d = h_string.split()
    if len(_d) == 2:
        try:
            n = float(_d[0]) * conv[_d[1]]
            return n
        except ValueError:
            raise ValueError('Invalid number to convert. 1st word is not a number', h_string)
        except KeyError:
            raise ValueError('Invalid number to convert. 2nd word should be either of M,B or T', h_string)
    else:
        raise ValueError('Invalid number to convert.There should be 2 words', h_string)

def insert_profile_data( cur_dict, json_wsj_profile ):
        # cur_dict['company'] = l.name
        # cur_dict['ticker'] = l.ticker
        # cur_dict['industry'] = json_data['Company Info']['Industry']
        # cur_dict['sector'] = json_data['Company Info']['Sector']


        cur_dict['type1'] = 'Profile'

        for h in json_wsj_profile['Company Info']:
            n_cur_dict = cur_dict.copy()
            n_cur_dict['type2'] = 'Company Info'
            n_cur_dict['type3'] = h
            n_cur_dict['value_string'] = json_wsj_profile['Company Info'][h]
            _string = json_wsj_profile['Company Info'][h].strip()
            try:
                # try with 68,000 ==> 68000
                n_cur_dict['val'] = float(_string.replace( ',', '' ))
            except ValueError:
                try:
                    #Percentage eg. 68% ==> 68
                    n_cur_dict['val'] = float(_string.replace( '%', '' ))
                except ValueError:
                    # try million billion. eg: 120 M ==< 120000000
                    try:
                        n_cur_dict['val'] = human_readable_nums_to_int( _string )
                    except ValueError:
                        None


            add_to_db(n_cur_dict)

        n_cur_dict = cur_dict.copy()
        n_cur_dict['type2'] = 'Contact Address'
        n_cur_dict['value_string'] = json_wsj_profile['Contact Address']
        add_to_db(n_cur_dict)


        n_cur_dict = cur_dict.copy()
        n_cur_dict['type2'] = 'Description'
        n_cur_dict['value_string'] = json_wsj_profile['Description']
        add_to_db(n_cur_dict)

        n_cur_dict = cur_dict.copy()
        n_cur_dict['type2'] = 'companyName'
        n_cur_dict['value_string'] = json_wsj_profile['companyName']
        add_to_db(n_cur_dict)

        n_cur_dict = cur_dict.copy()
        n_cur_dict['type2'] = 'tickerName'
        n_cur_dict['value_string'] = json_wsj_profile['tickerName']
        add_to_db(n_cur_dict)

        n_cur_dict = cur_dict.copy()
        n_cur_dict['type2'] = 'exchangeName'
        n_cur_dict['value_string'] = json_wsj_profile['exchangeName']
        add_to_db(n_cur_dict)



def insert_financials_data(base_dict, json_financials):
    base_dict['type1'] = 'Financials'
    for h1 in json_financials:
        for h2 in json_financials[h1]:
            n_cur_dict = base_dict.copy()
            n_cur_dict['type2']=h1
            n_cur_dict['type3']=h2
            v_string =  json_financials[h1][h2].strip()
            n_cur_dict['value_string'] = v_string
            try:
                n_cur_dict['val']= float(v_string.replace(',', '') )
            except ValueError:
                # Try split()
                try:
                    n_cur_dict['val'] = float( v_string.split()[0] )
                except ValueError:
                    # Try interpreting it as date
                    try:
                        n_cur_dict['val'] = datetime.strptime( v_string,  '%m/%d/%Y').strftime('%Y%m%d')
                    except:
                        pass

            add_to_db(n_cur_dict)


def insert_institutional_investors(base_dict, json_institutional_investor):
    base_dict['type1'] = 'Ownership'
    base_dict['type2'] = 'Institutional Investor'
    for owner in json_institutional_investor:
        for particulars in json_institutional_investor[owner]:
            np_cur_dict = base_dict.copy()
            np_cur_dict['type3'] = owner.strip()
            np_cur_dict['type4'] = particulars
            try:
                v_string = json_institutional_investor[owner][particulars].strip()
                np_cur_dict['value_string'] = v_string
                np_cur_dict['val'] = float(v_string.replace(',', '' ).replace( '%', '' ))
            except ValueError:
                #try interpreting it as a string
                np_cur_dict['val'] = datetime.strptime( v_string, '%m/%d/%y').strftime('%Y/%m/%d') #month/date/year
            except TypeError:
                pass
            add_to_db(np_cur_dict)



def insert_mutual_fund_owners(base_dict, json_mutual_fund_owners):
    base_dict['type1'] = 'Ownership'
    base_dict['type2'] = 'Mutual Funds'
    for owner in json_mutual_fund_owners:
        for particulars in json_mutual_fund_owners[owner]:
            np_cur_dict = base_dict.copy()
            np_cur_dict['type3'] = owner.strip()
            np_cur_dict['type4'] = particulars.strip()
            try:
                v_string = json_mutual_fund_owners[owner][particulars].strip()
                np_cur_dict['value_string'] = v_string
                np_cur_dict['val'] = float(v_string.replace(',', '' ).replace( '%', '' ))
            except ValueError:
                #try interpreting it as a string
                np_cur_dict['val'] = datetime.strptime( v_string, '%m/%d/%y').strftime('%Y/%m/%d') #month/date/year
            except TypeError:
                pass
            add_to_db(np_cur_dict)


def insert_executives_data(base_dict, json_executives):
    for i_str in json_executives:
        n_cur_dict = base_dict.copy()
        n_cur_dict['type1'] = 'Executives'
        n_cur_dict['type2'] = i_str.strip() +'#'+ json_executives[i_str]['Name']
        for attr in json_executives[i_str]:
            np_cur_dict = n_cur_dict.copy()
            np_cur_dict['type3'] = attr.strip()
            np_cur_dict['value_string'] = json_executives[i_str][attr].strip()
            try:
                np_cur_dict['val'] = int(json_executives[i_str][attr].strip().replace(',',''))
            except ValueError:
                np_cur_dict['val'] = 0
            add_to_db(np_cur_dict)



#-------------- Financial Statements Insertion ----------------#
def str_to_float( r ):
    try:
        r = r.strip().replace(',', '').replace('%','').strip()
    except:
        r = 'None'
    try:
        #try directly converting
        f = float(r)
        return f
    except ValueError:
        try:
            #try brackets eg: (4500)==> -4500
            f =  -float(str(r).translate(None,"(),"))
            # code.interact( local=locals() )
            return f
        except:
            return 0.0

# Million returns 1; Thousand returns 0.001; Billion returns 1000;
def get_multiplier( fiscal_str ):
    if fiscal_str.find('Million') > 0:
        return 1.0

    if fiscal_str.find('Thousand') > 0:
        return 0.001

    if fiscal_str.find('Billion') > 0:
        return 1000.

    return 1.1

## Inserts 1 sheet only
## statement_name : one of ('income_statement', 'balance_sheet', 'cash_flow_statement')
## base_dict : a copy of base_dict
## tag : eg: a.assets.2012, a.operating.2015, a.30-Jun-2014 etc
## json_loader_func : eg: wsj.load_json_cash_flow_statement etc
def insert_statement_data( statement_name, base_dict, tag, json_loader_func ):
    l2_dict = base_dict.copy()
    tag_components = tag.split( '.' )
    l2_dict['type1'] = 'Financial Statements'
    l2_dict['type2'] = str(statement_name)

    # this converts tag_components ==> (type2,type3,type4)
    if len(tag_components)==3: #for cashflow st. and balance sheet
        l2_dict['period'] = tag_components[0] # a
        l2_dict['type3'] = tag_components[1] # eg. assets
        try:
            l2_dict['type4'] = int(tag_components[2]) # 2013
        except:
            try:
                l2_dict['type4'] = int(datetime.strptime( tag_components[2], '%d-%b-%Y' ).strftime( '%Y%m%d' )) #30-Jun-2014
            except:
                l2_dict['type4'] = tag_components[2]
    elif len(tag_components)==2: #for income statement
        l2_dict['period'] = tag_components[0] # a
        l2_dict['type3'] = str(None)         # None, #TODO consider getting rid of these None. And then figure out howto do such queries. using None because it is convinient. SImilarly for others like type6, type7 etc
        try:
            l2_dict['type4'] = int(tag_components[1]) # 2013
        except:
            try:
                l2_dict['type4'] = int(datetime.strptime( tag_components[1], '%d-%b-%Y' ).strftime( '%Y%m%d' )) #30-Jun-2014
            except:
                l2_dict['type4'] = tag_components[1]
    else:
        __write( "FATAL ERROR : INVALID TAG" )


    A = json_loader_func( tag ) #note that these statements are having data in _E3M5_ tag

    try:
        fiscal_mul = get_multiplier( A['_FISCAL_NOTE_']['_E3M5_'] )
    except:
        fiscal_mul = -1.0 #this string does not exist

    # if l2_dict['ticker'] == '0048.HK':
        # code.interact( local=locals() )

    for h1 in A:
        if h1 == '_HEADER_': continue #avoid _HEADER_ / use it for verification
        # if h1 == '_FISCAL_NOTE_': continue #TODO
        l2_dict['type5'] = h1
        l2_dict['type6'] = str(None)
        l2_dict['type7'] = str(None)
        l2_dict['value_string'] = A[h1]['_E3M5_']
        l2_dict['val'] = str_to_float( A[h1]['_E3M5_'] )
        l2_dict['fiscal_mul'] = fiscal_mul
        add_to_db( l2_dict.copy() )
        for h2 in A[h1]:
            if h2 == '_E3M5_': continue #found data
            l2_dict['type5'] = h1
            l2_dict['type6'] = h2
            l2_dict['type7'] = str(None)
            l2_dict['value_string'] = A[h1][h2]['_E3M5_']
            l2_dict['val'] = str_to_float( A[h1][h2]['_E3M5_'] )
            add_to_db( l2_dict.copy() )
            for h3 in A[h1][h2]:
                if h3 == '_E3M5_': continue
                l2_dict['type5'] = h1
                l2_dict['type6'] = h2
                l2_dict['type7'] = h3
                l2_dict['value_string'] = A[h1][h2][h3]['_E3M5_']
                l2_dict['val'] = str_to_float( A[h1][h2][h3]['_E3M5_'] )
                add_to_db( l2_dict.copy() )


def insert_all_financial_sheets( s_wsj, base_dict ):
    loaders = {'income_statement':s_wsj.load_json_income_statement, \
               'balance_sheet': s_wsj.load_json_balance_sheet,\
               'cash_flow_statement': s_wsj.load_json_cash_flow_statement\
               }

    components = {'income_statement': [None], \
               'balance_sheet': ['assets', 'liabilities'],\
               'cash_flow_statement': ['operating', 'financing', 'investing']\
               }

    for period in ['a', 'q']:
        for st_name in loaders: #iterative over statement name
            for sub_st_name in components[st_name]: #iterate over sub-statement names
                tag_list = s_wsj.ls( period, st_name, sub_st_name)
                json_loader_func = loaders[st_name]

                for tag in tag_list: #iteraive over each sheet
                    insert_statement_data( st_name, base_dict.copy(), tag, json_loader_func )


# ------------------------- MAIN ----------------------------#

# Commandline Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument( '-ld', '--lists_db_dir', required=True, help='Specify lists DB directory (eg. equities_db/lists/)' )
parser.add_argument( '-v', '--verbosity', type=int, default=0, help='Verbosity 0 is quite. 5 is most verbose' )
parser.add_argument( '-db', '--data_dir', required=True, help='Specify database directory (eg. equities_db/data__N/)' )
parser.add_argument(  '--logfile', default=None, help='Logging file name' )
parser.add_argument(  '--logserver', default=None, help='Logging server. eg. localhost:9276' )
parser.add_argument(  '--mongodb', default=None, help='Specify mongodb instance. If not specified will use localhost:27017. eg mongodb://localhost:27017.' )

# Bourse
parser.add_argument( '--xhkex', default=False, action='store_true', help='List all HKEX Stocks' )
parser.add_argument( '--xbse', default=False, action='store_true', help='List all Bombay Stock Ex (BSE) Stocks' )
parser.add_argument( '--xnse', default=False, action='store_true', help='List all National Stock Ex India (NSE) Stocks' )
parser.add_argument( '--xnyse', default=False, action='store_true', help='List all New York Stock Exchange Stock (NYSE)' )
parser.add_argument( '--xnasdaq', default=False, action='store_true', help='List all NASDAQ Stocks' )
parser.add_argument( '--xamex', default=False, action='store_true', help='List all AMEX stocks' )
parser.add_argument( '--xtyo', default=False, action='store_true', help='List all Tokyo Ex Stocks' )
parser.add_argument( '--xsse', default=False, action='store_true', help='List all Shanghai Ex Stocks' )
parser.add_argument( '--xszse', default=False, action='store_true', help='List all Shenzen Ex Stocks' )


args = parser.parse_args()

if args.logfile is None:
    fp_logfile = sys.stdout
else:
    fp_logfile = open( args.logfile, 'w' )
    print 'LOGFILE NAME : ', args.logfile
    __write( '```\n' + ' '.join( sys.argv ) + '\n```' )

if args.logserver is None:
    fp_logserver = None
else:
    print 'LOGSERVER    : ', args.logserver
    try:
        _host = args.logserver.split(':')[0]
        _port = int(args.logserver.split(':')[1])
        fp_logserver = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        fp_logserver.connect( (_host,_port) )
        # fp_logserver.sendall( 'Connected!')
        log_server( 'Connected')
    except:
        print tcol.FAIL, 'Cannot connect to logserver', tcol.ENDC
        print 'Start a forked logserver like:'
        print '$ socat TCP4-LISTEN:9595,fork STDOUT'


if args.lists_db_dir:
    __write( tcol.HEADER+ 'lists_db_dir : '+ args.lists_db_dir+ tcol.ENDC )

if args.data_dir:
    __write( tcol.HEADER+ 'data_dir : '+ args.data_dir+ tcol.ENDC )

# if args.verbosity:
__write( tcol.HEADER+ 'verbosity : '+ str(args.verbosity)+ tcol.ENDC )



# Setup DB access and file accesses
if args.mongodb is None:
    __write( tcol.HEADER + 'Mongo-Server: ' + 'mongodb://localhost:27017/' + tcol.ENDC )
    client = pymongo.MongoClient()
else:
    __write( tcol.HEADER + 'Mongo-Server: ' + args.mongodb +  tcol.ENDC )
    client = pymongo.MongoClient(args.mongodb)

pprint.pprint(  client.server_info()  ) # The process will fail if cannot connect to mongodb


db = client.universalData

# lister = TickerLister( args.lists_db_dir )
# full_list = []
# full_list += lister.list_full_hkex( use_cached=True)#[40:60]
# full_list += lister.list_full_bse( use_cached=True )#[1500:]
# full_list += lister.list_full_nse( use_cached=True )#[0:100]

# Get List
lister = TickerLister( args.lists_db_dir )
full_list = []
n=3
__write( tcol.HEADER+ ' : Exchanges :'+ tcol.ENDC )
if args.xhkex:
    __write( tcol.HEADER+ '\t(HKEX) Hong Kong Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_hkex( use_cached=True)#[0:n]
if args.xbse:
    __write( tcol.HEADER+ '\t(BSE) Bombay Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_bse( use_cached=True )#[0:n]
if args.xnse:
    __write( tcol.HEADER+ '\t(NSE) National Stock Exchange of India'+ tcol.ENDC )
    full_list += lister.list_full_nse( use_cached=True )#[0:n]
if args.xnyse:
    __write( tcol.HEADER+ '\t(NYSE) New York Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_nyse( use_cached=True )#[0:n]
if args.xnasdaq:
    __write( tcol.HEADER+ '\t(NASDAQ) NASDAQ, USA'+ tcol.ENDC )
    full_list += lister.list_full_nasdaq( use_cached=True )#[0:n]
if args.xamex:
    __write( tcol.HEADER+ '\t(AMEX) American Stock Exchange'+ tcol.ENDC )
    full_list += lister.list_full_amex( use_cached=True )#[0:n]
if args.xtyo:
    __write( tcol.HEADER+ '\t(TYO) Japan Exchange Group, Tokyo'+ tcol.ENDC )
    full_list += lister.list_full_tyo( use_cached=True )#[0:n]
if args.xsse:
    __write( tcol.HEADER+ '\t(SH) Shanghai Stock Exchange, China'+ tcol.ENDC )
    full_list += lister.list_full_sse( use_cached=True )#[0:n]
if args.xszse:
    __write( tcol.HEADER+ '\t(SZ) Shenzen Stock Exchange, China'+ tcol.ENDC )
    full_list += lister.list_full_szse( use_cached=True )#[0:n]



# db_prefix = 'equities_db/data__N/'
db_prefix = args.data_dir


# Loop Over the list
cur_dict = {}

total_fail = 0
total_ok = 0
per_ticker_fail = 0
per_ticker_ok = 0

# l = full_list[9]
startTimeTotal = time.time()
proc_started = datetime.now()
for i,l in enumerate(full_list):
    per_ticker_fail = 0
    per_ticker_ok = 0

    startTime = time.time()
    folder = db_prefix+'/'+l.ticker+'/'
    __write( tcol.OKGREEN+ str(i)+' of %d ' %(len(full_list))+ str(l)+ tcol.ENDC )
    log_server( tcol.OKGREEN+ str(i)+' of %d ' %(len(full_list))+ str(l)+ tcol.ENDC )

    s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder, verbosity=args.verbosity, logfile=fp_logfile)
    json_wsj_profile = s_wsj.load_json_profile()
    json_financials = s_wsj.load_financials()

    if json_wsj_profile is None or json_financials is None:
        continue

    # Base structure
    base_dict = {}
    base_dict['bourse'] = l.ticker.split('.')[-1]
    base_dict['company'] = l.name
    base_dict['ticker'] = l.ticker
    base_dict['industry'] = json_wsj_profile['Company Info']['Industry']
    base_dict['sector'] = json_wsj_profile['Company Info']['Sector']

    #
    # Profile Data
    insert_profile_data(base_dict.copy(), json_wsj_profile)

    #
    # Financial Overview
    insert_financials_data( base_dict.copy(), json_financials )


    #
    # Institutional Investors
    json_institutional_investor = s_wsj.load_institutional_investors()
    if json_institutional_investor is not None:
        insert_institutional_investors( base_dict.copy(), json_institutional_investor )


    #
    # Mutual Funds that Own this share
    json_mutual_fund_owners = s_wsj.load_mututal_fund_owners()
    if json_mutual_fund_owners is not None:
        insert_mutual_fund_owners(base_dict.copy(), json_mutual_fund_owners )


    #
    # Executives
    # s_reuters = SourceReuters( ticker=l.ticker, stock_prefix=folder, verbosity=0 )
    # json_executives = s_reuters.load_executives()
    # if json_executives is not None:
    #     insert_executives_data( base_dict.copy(), json_executives )


    #
    # Financial Statements
    insert_all_financial_sheets( s_wsj, base_dict.copy() )

    __write( 'Inserts Succeed : %d, Inserts Failed : %d' %(per_ticker_ok, per_ticker_fail) )
    __write( 'Time taken for %s : %4.2fs' %(l.ticker, time.time() - startTime ) )

__write(  tcol.OKGREEN+'Total Inserts Succeed : %d, Total Inserts Failed : %d' %(total_ok, total_fail) + tcol.ENDC )
__write( tcol.OKGREEN+ 'PID: '+ str(os.getpid())+ tcol.ENDC )
__write( tcol.OKGREEN+ 'Started  on '+ str(proc_started)+ tcol.ENDC )
__write( tcol.OKGREEN+ 'Finished on '+ str(datetime.now())+ tcol.ENDC )
__write( 'Total Time taken : %4.2fs' %(time.time() - startTimeTotal) )

log_server(  tcol.OKGREEN+'Total Inserts Succeed : %d, Total Inserts Failed : %d' %(total_ok, total_fail) + tcol.ENDC )
log_server( tcol.OKGREEN+ 'Started  on '+ str(proc_started)+ tcol.ENDC )
log_server( tcol.OKGREEN+ 'Finished on '+ str(datetime.now())+ tcol.ENDC )
log_server( 'Total Time taken : %4.2fs' %(time.time() - startTimeTotal) )
# solr_commit()
