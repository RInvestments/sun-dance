""" Insert functions for aastock data.

    This script goes over all the HKEX list and loads
    the json files (hardcoded in this script). This needs to be
    compatible with SourceAAStocks.py.

    Ideally should start a subpackage of inserters. But add-hoc
    inserters are also just fine. If you have time for this do it
    else no priority on it.

        Author  : Manohar Kuse <mpkuse@connect.ust.hk>
        Created : 14th Dec, 2017
"""




import sys
import os.path
import urllib2
# import pprint
import os
import locale
import json
import collections

import time
from datetime import datetime

import TerminalColors
tcol = TerminalColors.bcolors()

import argparse
import urllib2
import uuid
import pymongo
import code


from stockspotter.lister.TickerLister import TickerLister
from stockspotter.db.SourceAAStocks import SourceAAStocks

def __write( msg ):
    # print msg
    fp_logfile.write( msg +'\n')

def log_debug( msg, lvl=1 ):
    if lvl in range( args.verbosity ):
        __write( '[DEBUG=%d]' %(lvl)+msg )


def get_uuid( cur_dict ):
    od = collections.OrderedDict(sorted(cur_dict.items()))

    json_data_obj =  json.dumps(od)
    digest = uuid.uuid3(uuid.NAMESPACE_DNS, json_data_obj)
    return str(digest)

def add_to_db( curr_dict ):
    global total_ok, total_fail

    curr_dict['id'] = get_uuid( curr_dict )
    curr_dict['last_modified'] = datetime.now()

    try:
        db.aastocks_corp_profile.insert( curr_dict )
        total_ok += 1
    except pymongo.errors.DuplicateKeyError, e:
        # print 'DuplicateKeyError'
        total_fail+=1
    except:
        # print 'Fail'
        total_fail+=1



# ------------------------- MAIN ----------------------------#

# To load from commandline
parser = argparse.ArgumentParser()
parser.add_argument( '-v', '--verbosity', type=int, default=0, help='Verbosity 0 is quite. 5 is most verbose' )
parser.add_argument(  '--logfile', default=None, help='Logging file name' )
parser.add_argument( '-ld', '--lists_db_dir', required=True, help='Specify lists DB directory (eg. equities_db/lists/)' )
parser.add_argument( '-db', '--data_dir', required=True, help='Specify database directory (eg. equities_db/data__N/)' )
args = parser.parse_args()

if args.logfile is None:
    fp_logfile = sys.stdout
else:
    fp_logfile = open( args.logfile, 'w' )
    print 'LOGFILE NAME : ', args.logfile
    __write( '```\n' + ' '.join( sys.argv ) + '\n```' )

if args.lists_db_dir:
    __write( tcol.HEADER+ 'lists_db_dir : '+ args.lists_db_dir+ tcol.ENDC )

if args.data_dir:
    __write( tcol.HEADER+ 'data_dir : '+ args.data_dir+ tcol.ENDC )

# if args.verbosity:
__write( tcol.HEADER+ 'verbosity : '+ str(args.verbosity)+ tcol.ENDC )


db_prefix = args.data_dir #'equities_db/test_db/'
list_db =  args.lists_db_dir #'equities_db/lists/'

total_ok = 0
total_fail = 0

# Setup Lister
lister = TickerLister( list_db )
full_list = lister.list_full_hkex( use_cached=True)#[0:50]

# MongoDB
client = pymongo.MongoClient()
db = client.sun_dance


# The Loop
startTimeTotal = time.time()
proc_started = datetime.now()
for i,l in enumerate(full_list):
    # print '=== ', i, l.ticker, l.name, ' ==='
    startTime = time.time()

    __write( tcol.OKGREEN+ str(i)+' of %d ' %(len(full_list))+ str(l)+ tcol.ENDC )


    folder = db_prefix+'/'+l.ticker+'/'

    s_aastocks = SourceAAStocks( l.ticker, folder, 0 )
    json_data = s_aastocks.open_detailed_company_profile_json()

    if json_data is not None:
        json_data['ticker'] = l.ticker
        json_data['name'] = l.name

        __write( '  Chairman: %s' %(json_data['Chairman']) )
        add_to_db( json_data )

    __write( 'Time taken for %s : %4.2fs' %(l.ticker, time.time() - startTime ) )


__write(  tcol.OKGREEN+'Total Inserts Succeed : %d, Total Inserts Failed : %d' %(total_ok, total_fail) + tcol.ENDC )
__write( tcol.OKGREEN+ 'PID: '+ str(os.getpid())+ tcol.ENDC )
__write( tcol.OKGREEN+ 'Started  on '+ str(proc_started)+ tcol.ENDC )
__write( tcol.OKGREEN+ 'Finished on '+ str(datetime.now())+ tcol.ENDC )
__write( 'Total Time taken : %4.2fs' %(time.time() - startTimeTotal) )
