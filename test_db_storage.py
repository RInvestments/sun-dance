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



    ########################
    #### Solr Insertion ####
    ########################
    req = urllib2.Request(url='http://localhost:8983/solr/universalData/update/json/docs',
                          data=json_cur_dict)

    req.add_header('Content-type', 'application/json')
    f = urllib2.urlopen(req)
    print 'Solr Response : ', f.read()



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


def modi_safai_abhiyan():
    req = urllib2.Request(url='http://localhost:8983/solr/universalData/update?commit=true')
    f = urllib2.urlopen(req)
    print f.read()
    print "safai puri hui, jilo !!!"

def module1( json_data ):
        cur_dict['company'] = l.name
        cur_dict['ticker'] = l.ticker
        cur_dict['industry'] = json_data['Company Info']['Industry']
        cur_dict['sector'] = json_data['Company Info']['Sector']
        cur_dict['type1'] = 'Profile'
        cur_dict['type2'] = 'Company Info'
        cur_dict['type3'] = 'Employees'

        try:
            cur_dict['val'] = int(json_data['Company Info']['Employees'].replace( ',', '' ))
        except ValueError:
            cur_dict['val'] =  0

        add_to_db(cur_dict.copy())

# def module2( json)

lister = TickerLister( 'equities_db/lists/' )
full_list = lister.list_full_hkex( use_cached=True)
db_prefix = 'equities_db/data__20170316'



cur_dict = {}

# l = full_list[9]
for l in full_list:
    folder = db_prefix+'/'+l.ticker+'/'
    s_wsj = SourceWSJ( ticker=l.ticker, stock_prefix=folder, verbosity=0 )
    json_data = s_wsj.load_json_profile()
    json_data_financials = s_wsj.load_financials()
    if json_data is None or json_data_financials is None:
        continue

    cur_dict['company'] = l.name
    cur_dict['ticker'] = l.ticker
    cur_dict['industry'] = json_data['Company Info']['Industry']
    cur_dict['sector'] = json_data['Company Info']['Sector']
    cur_dict['type1'] = 'Financials'

    module1(json_data)

    #print json.dumps( json_data_financials, indent=4 )
    for ty1 in json_data_financials:
        for ty2 in json_data_financials[ty1]:
            #print ty1, '::', ty2, ':::', json_data_financials[ty1][ty2]
            n_cur_dict = cur_dict.copy()
            n_cur_dict['type2']=ty1
            n_cur_dict['type3']=ty2
            try:
                n_cur_dict['val']= float(json_data_financials[ty1][ty2].strip().replace(',', '') )
                add_to_db(n_cur_dict)
                n_cur_dict = None
            except ValueError:
                print "Value Error"


modi_safai_abhiyan()
