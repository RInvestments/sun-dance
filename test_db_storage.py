import sys
import os.path
import urllib2
import pprint
import os
import locale
import json
import collections

import time
from datetime import datetime

import TerminalColors
tcol = TerminalColors.bcolors()

from stockspotter.db.SourceHKEXProfile import SourceHKEXProfile
from stockspotter.db.SourceWSJ import SourceWSJ
from stockspotter.db.SourceReuters import SourceReuters
from stockspotter.lister.TickerLister import TickerLister

import urllib2
import uuid
import pymongo
import code

client = pymongo.MongoClient()
db = client.universalData



def get_uuid( cur_dict ):
    od = collections.OrderedDict(sorted(cur_dict.items()))

    json_data_obj =  json.dumps(od)
    # print json_data_obj
    # print type(json_data_obj)
    digest = uuid.uuid3(uuid.NAMESPACE_DNS, json_data_obj)
    return str(digest)

def add_to_db(cur_dict):
    #global db

    cur_dict['id'] = get_uuid( cur_dict )
    json_cur_dict = json.dumps(cur_dict)

    # print str(cur_dict)


    #
    # ########################
    # #### Solr Insertion ####
    # ########################
    # req = urllib2.Request(url='http://localhost:8983/solr/universalData/update/json/docs',
    #                       data=json_cur_dict)
    #
    # req.add_header('Content-type', 'application/json')
    # f = urllib2.urlopen(req)
    # print 'Solr Response : ', f.read()



    ###########################
    #### MongoDB Insertion ####
    ###########################

    #code.interact(local=locals())

    try:
        cur_dict['last_modified'] = datetime.now()
        db.universalData.insert( cur_dict )
    except Exception as e:
        print str(e)
        print tcol.FAIL, 'MOngoDB insert failed', tcol.ENDC

    del cur_dict


def solr_commit():
    req = urllib2.Request(url='http://localhost:8983/solr/universalData/update?commit=true')
    f = urllib2.urlopen(req)
    print f.read()
    print "Solr Commit Done !!!"

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
            try:
                n_cur_dict['value_string'] = json_wsj_profile['Company Info'][h]
                n_cur_dict['val'] = float(json_wsj_profile['Company Info'][h].strip().replace( ',', '' ))
            except ValueError:
                n_cur_dict['val'] =  0
            add_to_db(n_cur_dict)

        n_cur_dict = cur_dict.copy()
        n_cur_dict['type2'] = 'Contact Address'
        n_cur_dict['value_string'] = json_wsj_profile['Contact Address']
        add_to_db(n_cur_dict)


        n_cur_dict = cur_dict.copy()
        n_cur_dict['type2'] = 'Description'
        n_cur_dict['value_string'] = json_wsj_profile['Description']
        add_to_db(n_cur_dict)



def insert_financials_data(base_dict, json_financials):
    base_dict['type1'] = 'Financials'
    for h1 in json_financials:
        for h2 in json_financials[h1]:
            #print ty1, '::', ty2, ':::', json_data_financials[ty1][ty2]
            n_cur_dict = base_dict.copy()
            n_cur_dict['type2']=h1
            n_cur_dict['type3']=h2
            try:
                n_cur_dict['value_string'] = json_financials[h1][h2].strip()
                n_cur_dict['val']= float(json_financials[h1][h2].strip().replace(',', '') )
            except ValueError:
                # print "Value Error"
                n_cur_dict['val'] = 0
            add_to_db(n_cur_dict)


lister = TickerLister( 'equities_db/lists/' )
full_list = lister.list_full_hkex( use_cached=False)
db_prefix = 'equities_db/data__20170316'



cur_dict = {}

# l = full_list[9]
startTimeTotal = time.time()
for i,l in enumerate(full_list):
    startTime = time.time()
    folder = db_prefix+'/'+l.ticker+'/'
    print tcol.OKGREEN, i,'of %d' %(len(full_list)), l, tcol.ENDC

    s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder, verbosity=0 )
    json_wsj_profile = s_wsj.load_json_profile()
    json_financials = s_wsj.load_financials()

    if json_wsj_profile is None or json_financials is None:
        continue

    # Base structure
    base_dict = {}
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
        n_cur_dict = base_dict.copy()
        n_cur_dict['type1'] = 'Ownership'
        n_cur_dict['type2'] = 'Institutional Investor'
        for owner in json_institutional_investor:
            np_cur_dict = n_cur_dict.copy()
            for particulars in json_institutional_investor[owner]:
                np_cur_dict['type3'] = owner.strip()
                np_cur_dict['type4'] = particulars
                np_cur_dict['value_string'] = json_institutional_investor[owner][particulars].strip()
                add_to_db(np_cur_dict.copy())

    #
    # Mutual Funds that Own this share
    json_mutual_fund_owners = s_wsj.load_mututal_fund_owners()
    if json_mutual_fund_owners is not None:
        n_cur_dict = base_dict.copy()
        n_cur_dict['type1'] = 'Ownership'
        n_cur_dict['type2'] = 'Mutual Funds'
        for owner in json_mutual_fund_owners:
            np_cur_dict = n_cur_dict.copy()
            for particulars in json_mutual_fund_owners[owner]:
                np_cur_dict['type3'] = owner.strip()
                np_cur_dict['type4'] = particulars.strip()
                np_cur_dict['value_string'] = json_mutual_fund_owners[owner][particulars].strip()
                add_to_db(np_cur_dict.copy())


    #
    # Executives
    s_reuters = SourceReuters( ticker=l.ticker, stock_prefix=folder, verbosity=0 )
    json_executives = s_reuters.load_executives()
    if json_executives is not None:
        for i_str in json_executives:
            n_cur_dict = base_dict.copy()
            n_cur_dict['type1'] = 'Executives'
            n_cur_dict['type2'] = i_str.strip() # json_executives[i_str]['Name']
            for attr in json_executives[i_str]:
                np_cur_dict = n_cur_dict.copy()
                np_cur_dict['type3'] = attr.strip()
                np_cur_dict['value_string'] = json_executives[i_str][attr].strip()
                try:
                    np_cur_dict['val'] = int(json_executives[i_str][attr].strip().replace(',',''))
                except ValueError:
                    np_cur_dict['val'] = 0
                add_to_db(np_cur_dict.copy())
                # print json_executives[i_str][attr]






    print 'Time taken for %s : %4.2fs' %(l.ticker, time.time() - startTime )

print 'Total Time taken : %4.2fs' %(time.time() - startTimeTotal)

# solr_commit()
