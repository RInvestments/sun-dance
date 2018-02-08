""" Script for parsing the config file for actions and performing the actions
    in multiple processes. Typically this script will call data_retriver, data_parser,
    data_inserter.

    Typical Usage:
        sundance -f config/retrive_wsj.config.xml
"""

from lxml import etree
import argparse

import subprocess
import multiprocessing

import time
from datetime import datetime
from datetime import timedelta
import sys

import threading
import Queue
import code

import TerminalColors
tcol = TerminalColors.bcolors()

def _error( msg ):
    print tcol.FAIL, '[ERROR] ', msg, tcol.ENDC

def _debug( msg, lvl=1 ):
    if lvl in range( DEBUG_LEVEL ):
        print '[DEBUG=%d] ' %(lvl), msg

def _printer( msg ):
    print msg

def _isnum( s ):
    try:
        float(s)
        return True
    except ValueError:
        return False

class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.

    This class courtesy of :
    http://stefaanlippens.net/python-asynchronous-subprocess-pipe-reading/
    '''

    def __init__(self, fd, queue):
        assert isinstance(queue, Queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()
#
#
# def config_to_cmd( fname, store_dir=None ):
#     _debug( 'Open XML config : %s' %(fname) )
#
#     if store_dir is None:
#         _debug( 'will use store_dir from configxml file')
#     else:
#         _debug( 'store_dir: %s' %(store_dir) )
#
#     doc = etree.parse( fname )
#     global_ele = doc.find( 'global' )
#
#     # Iterate over each process
#     cmd_list = []
#     print 'Found %d process' %( len(doc.findall( 'process' )) )
#     for p in doc.findall( 'process' ):
#         # _debug( '---', 2 )
#
#         if p.find( 'type' ).text.strip() == 'retriver':
#
#             if store_dir is None:
#                 # Store DIR
#                 try:
#                     store_dir = p.find( 'store_dir' ).text.strip()
#                 except:
#                     store_dir = global_ele.find( 'store_dir' ).text.strip()
#
#             # List DIR
#             try:
#                 list_db = p.find( 'list_db' ).text.strip()
#             except:
#                 list_db = global_ele.find( 'list_db' ).text.strip()
#
#             # Verbosity
#             try:
#                 verbosity = int( p.find( 'verbosity' ).text.strip() )
#             except:
#                 try:
#                     verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
#                 except:
#                     verbosity = 0
#
#             # Data Source
#             task = p.find( 'task' ).text.strip()
#             task_arg = ''
#             for src in task.split( ',' ):
#                 task_arg += ' --%s ' %(src.strip())
#
#
#
#             # Exchange
#             exchange = p.find( 'exchange' ).text.strip()
#             exchange_arg = ''
#             for ex in exchange.split(','):
#                 exchange_arg += ' --%s ' %(ex.strip())
#
#
#             cmd = 'python data_retriver.py -sd %s -ld %s %s %s -v %d' %(store_dir, list_db, task_arg, exchange_arg, verbosity )
#             _debug( cmd, 2 )
#             cmd_list.append( cmd )
#
#
#
#         if p.find( 'type' ).text.strip() == 'parser':
#             if store_dir is None:
#                 # Store DIR
#                 try:
#                     store_dir = p.find( 'store_dir' ).text.strip()
#                 except:
#                     store_dir = global_ele.find( 'store_dir' ).text.strip()
#
#             # List DIR
#             try:
#                 list_db = p.find( 'list_db' ).text.strip()
#             except:
#                 list_db = global_ele.find( 'list_db' ).text.strip()
#
#             # Verbosity
#             try:
#                 verbosity = int( p.find( 'verbosity' ).text.strip() )
#             except:
#                 try:
#                     verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
#                 except:
#                     verbosity = 0
#
#             # Data Source
#             task = p.find( 'task' ).text.strip()
#             task_arg = ''
#             for src in task.split( ',' ):
#                 task_arg += ' --%s ' %(src.strip())
#
#
#
#             # Exchange
#             exchange = p.find( 'exchange' ).text.strip()
#             exchange_arg = ''
#             for ex in exchange.split(','):
#                 exchange_arg += ' --%s ' %(ex.strip())
#
#
#             cmd = 'python data_parser.py -sd %s -ld %s %s %s -v %d' %(store_dir, list_db, task_arg, exchange_arg, verbosity )
#             _debug( cmd , 2)
#             cmd_list.append( cmd )
#
#
#
#         if p.find( 'type' ).text.strip() == 'inserter':
#             # Store DIR
#             if store_dir is None:
#                 try:
#                     store_dir = p.find( 'store_dir' ).text.strip()
#                 except:
#                     store_dir = global_ele.find( 'store_dir' ).text.strip()
#
#             # List DIR
#             try:
#                 list_db = p.find( 'list_db' ).text.strip()
#             except:
#                 list_db = global_ele.find( 'list_db' ).text.strip()
#
#             # Verbosity
#             try:
#                 verbosity = int( p.find( 'verbosity' ).text.strip() )
#             except:
#                 try:
#                     verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
#                 except:
#                     verbosity = 0
#
#
#             # Exchange
#             exchange = p.find( 'exchange' ).text.strip()
#             exchange_arg = ''
#             for ex in exchange.split(','):
#                 exchange_arg += ' --%s ' %(ex.strip())
#
#
#             cmd = 'python data_inserter.py -db %s -ld %s %s -v %d' %(store_dir, list_db, exchange_arg, verbosity )
#             _debug( cmd, 2)
#             cmd_list.append( cmd )
#
#
#         if p.find( 'type' ).text.strip() == 'quote_inserter':
#             if store_dir is None:
#                 # Store DIR
#                 try:
#                     store_dir = p.find( 'store_dir' ).text.strip()
#                 except:
#                     store_dir = global_ele.find( 'store_dir' ).text.strip()
#
#             # List DIR
#             try:
#                 list_db = p.find( 'list_db' ).text.strip()
#             except:
#                 list_db = global_ele.find( 'list_db' ).text.strip()
#
#             # Verbosity
#             try:
#                 verbosity = int( p.find( 'verbosity' ).text.strip() )
#             except:
#                 try:
#                     verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
#                 except:
#                     verbosity = 0
#
#
#
#             # Exchange
#             exchange = p.find( 'exchange' ).text.strip()
#             exchange_arg = ''
#             for ex in exchange.split(','):
#                 exchange_arg += ' --%s ' %(ex.strip())
#
#
#             cmd = 'python daily_quote_inserter.py -db %s -ld %s %s -v %d' %(store_dir, list_db, exchange_arg, verbosity )
#             _debug( cmd, 2 )
#             cmd_list.append( cmd )
#
#         if p.find( 'type' ).text.strip() == 'aastocks_inserter':
#             if store_dir is None:
#                 try:
#                     store_dir = p.find( 'store_dir' ).text.strip()
#                 except:
#                     store_dir = global_ele.find( 'store_dir' ).text.strip()
#
#             # List DIR
#             try:
#                 list_db = p.find( 'list_db' ).text.strip()
#             except:
#                 list_db = global_ele.find( 'list_db' ).text.strip()
#
#             # Verbosity
#             try:
#                 verbosity = int( p.find( 'verbosity' ).text.strip() )
#             except:
#                 try:
#                     verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
#                 except:
#                     verbosity = 0
#
#             cmd = 'python aastocks_inserter.py -db %s -ld %s -v %d' %(store_dir, list_db, verbosity )
#             _debug( cmd, 2 )
#             cmd_list.append( cmd )
#
#
#
#
#     # Log dir
#     if store_dir is None:
#         try:
#             log_dir = global_ele.find( 'log_dir' ).text.strip()
#         except:
#             try:
#                 log_dir = global_ele.find( 'store_dir' ).text.strip()
#             except:
#                 log_dir = '/tmp/'
#     else:
#         log_dir = store_dir+'/'
#
#     return cmd_list, log_dir+str(p.find( 'type' ).text.strip())+'_'
#     # return cmd_list, log_dir
#

def processgroup_2_cmd( group, global_ele, store_dir=None ):
    """
        This function expects the XML sub-tree.
    """
    if store_dir is None:
        _debug( 'will use store_dir from configxml file')
    else:
        _debug( 'store_dir: %s' %(store_dir) )


    # Iterate over each process
    cmd_list = []
    _debug( 'Found %d process in this group' %( len(group.findall( 'process' )) ) )
    for p in group.findall( 'process' ):
        # _debug( '---', 2 )

        if p.find( 'type' ).text.strip() == 'retriver':

            if store_dir is None:
                # Store DIR
                try:
                    store_dir = p.find( 'store_dir' ).text.strip()
                except:
                    store_dir = global_ele.find( 'store_dir' ).text.strip()

            # List DIR
            try:
                list_db = p.find( 'list_db' ).text.strip()
            except:
                list_db = global_ele.find( 'list_db' ).text.strip()

            # Verbosity
            try:
                verbosity = int( p.find( 'verbosity' ).text.strip() )
            except:
                try:
                    verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
                except:
                    verbosity = 0

            # Data Source
            task = p.find( 'task' ).text.strip()
            task_arg = ''
            for src in task.split( ',' ):
                task_arg += ' --%s ' %(src.strip())



            # Exchange
            exchange = p.find( 'exchange' ).text.strip()
            exchange_arg = ''
            for ex in exchange.split(','):
                exchange_arg += ' --%s ' %(ex.strip())


            cmd = 'python data_retriver.py -sd %s -ld %s %s %s -v %d' %(store_dir, list_db, task_arg, exchange_arg, verbosity )
            _debug( cmd, 2 )
            cmd_list.append( cmd )



        if p.find( 'type' ).text.strip() == 'parser':
            if store_dir is None:
                # Store DIR
                try:
                    store_dir = p.find( 'store_dir' ).text.strip()
                except:
                    store_dir = global_ele.find( 'store_dir' ).text.strip()

            # List DIR
            try:
                list_db = p.find( 'list_db' ).text.strip()
            except:
                list_db = global_ele.find( 'list_db' ).text.strip()

            # Verbosity
            try:
                verbosity = int( p.find( 'verbosity' ).text.strip() )
            except:
                try:
                    verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
                except:
                    verbosity = 0

            # Data Source
            task = p.find( 'task' ).text.strip()
            task_arg = ''
            for src in task.split( ',' ):
                task_arg += ' --%s ' %(src.strip())



            # Exchange
            exchange = p.find( 'exchange' ).text.strip()
            exchange_arg = ''
            for ex in exchange.split(','):
                exchange_arg += ' --%s ' %(ex.strip())


            cmd = 'python data_parser.py -sd %s -ld %s %s %s -v %d' %(store_dir, list_db, task_arg, exchange_arg, verbosity )
            _debug( cmd , 2)
            cmd_list.append( cmd )



        if p.find( 'type' ).text.strip() == 'inserter':
            # Store DIR
            if store_dir is None:
                try:
                    store_dir = p.find( 'store_dir' ).text.strip()
                except:
                    store_dir = global_ele.find( 'store_dir' ).text.strip()

            # List DIR
            try:
                list_db = p.find( 'list_db' ).text.strip()
            except:
                list_db = global_ele.find( 'list_db' ).text.strip()

            # Verbosity
            try:
                verbosity = int( p.find( 'verbosity' ).text.strip() )
            except:
                try:
                    verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
                except:
                    verbosity = 0


            # Exchange
            exchange = p.find( 'exchange' ).text.strip()
            exchange_arg = ''
            for ex in exchange.split(','):
                exchange_arg += ' --%s ' %(ex.strip())


            cmd = 'python data_inserter.py -db %s -ld %s %s -v %d' %(store_dir, list_db, exchange_arg, verbosity )
            _debug( cmd, 2)
            cmd_list.append( cmd )


        if p.find( 'type' ).text.strip() == 'quote_inserter':
            if store_dir is None:
                # Store DIR
                try:
                    store_dir = p.find( 'store_dir' ).text.strip()
                except:
                    store_dir = global_ele.find( 'store_dir' ).text.strip()

            # List DIR
            try:
                list_db = p.find( 'list_db' ).text.strip()
            except:
                list_db = global_ele.find( 'list_db' ).text.strip()

            # Verbosity
            try:
                verbosity = int( p.find( 'verbosity' ).text.strip() )
            except:
                try:
                    verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
                except:
                    verbosity = 0



            # Exchange
            exchange = p.find( 'exchange' ).text.strip()
            exchange_arg = ''
            for ex in exchange.split(','):
                exchange_arg += ' --%s ' %(ex.strip())


            cmd = 'python daily_quote_inserter.py -db %s -ld %s %s -v %d' %(store_dir, list_db, exchange_arg, verbosity )
            _debug( cmd, 2 )
            cmd_list.append( cmd )

        if p.find( 'type' ).text.strip() == 'aastocks_inserter':
            if store_dir is None:
                try:
                    store_dir = p.find( 'store_dir' ).text.strip()
                except:
                    store_dir = global_ele.find( 'store_dir' ).text.strip()

            # List DIR
            try:
                list_db = p.find( 'list_db' ).text.strip()
            except:
                list_db = global_ele.find( 'list_db' ).text.strip()

            # Verbosity
            try:
                verbosity = int( p.find( 'verbosity' ).text.strip() )
            except:
                try:
                    verbosity = int( global_ele.find( 'verbosity' ).text.strip() )
                except:
                    verbosity = 0

            cmd = 'python aastocks_inserter.py -db %s -ld %s -v %d' %(store_dir, list_db, verbosity )
            _debug( cmd, 2 )
            cmd_list.append( cmd )




    # Log dir
    if store_dir is None:
        try:
            log_dir = global_ele.find( 'log_dir' ).text.strip()
        except:
            try:
                log_dir = global_ele.find( 'store_dir' ).text.strip()
            except:
                log_dir = '/tmp/'
    else:
        log_dir = store_dir

    try:
        full_log_dir = log_dir+'/'+group.attrib['id'].strip()
    except:
        try:
            full_log_dir = log_dir+'/'+str(p.find( 'type' ).text.strip())+'_'
        except:
            RANDOM_STRING = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            full_log_dir = log_dir+'/'+str( RANDOM_STRING )+'_'

    return cmd_list,full_log_dir
    # return cmd_list, log_dir


def consolidated_config_to_cmd( fname, store_dir ):
    #
    # Read global info
    _printer( tcol.HEADER+'Open XML config : %s' %(fname)+tcol.ENDC )
    _debug( 'Open XML config : %s' %(fname) )

    if store_dir is None:
        _debug( 'will use store_dir from configxml file')
    else:
        _debug( 'store_dir: %s' %(store_dir) )

    doc = etree.parse( fname )
    global_ele = doc.find( 'global' )
    if global_ele is None:
        _error( 'Cannot find tag global (required)' )
        quit()


    #
    # Read Groups
    all_groups = doc.findall( 'group' )
    _printer( tcol.HEADER+'Reading <group>s'+ tcol.ENDC )
    _printer( 'Total groups :'+ str(len( all_groups )) )

    proc_tree = {}
    if len(all_groups) == 0: # File does not have a group structure and it process-flat structure (older version)
        _printer( 'File does not have a <group> structure. Collecting all <process> to execute in parallel')
        _debug( 'File does not have a <group> structure. Collecting all <process> to execute in parallel')
        cmd, log_dir = processgroup_2_cmd( doc, global_ele, store_dir )
        for _c in cmd:
            _printer( '    '+_c)
        _printer( tcol.OKGREEN+'OK!'+tcol.ENDC )
        return [(cmd, log_dir)], None
    else:
        for group_i, group in enumerate(all_groups):
            _printer( '  group#%3d, id=%s' %(  group_i, group.attrib['id'].strip() ) )
            cmd, log_dir = processgroup_2_cmd( group, global_ele, store_dir )
            for _c in cmd:
                _printer( '    '+_c)
            if group.attrib['id'].strip() in proc_tree.keys():
                _error( 'Repeated id. Groups need to have unique IDs. Please rectify the XML')
                quit()
            proc_tree[ group.attrib['id'].strip() ] = (cmd, log_dir)


    _printer( tcol.OKGREEN+'<group>s OK!'+tcol.ENDC )

    #
    # Read <execution>
    try:
        _printer( tcol.HEADER+'Reading <execution>s'+tcol.ENDC )
        execution_tag = doc.find( 'execution' )
        all_lines = execution_tag.findall( 'line' )
        _printer( 'Total execution lines:'+ str( len( all_lines ) ) )
    except:
        _error( 'Fail! Cannot find <execution> tag (required)')
        quit()

    # Check if everything can be executed
    status = True
    for line_i, line in enumerate(all_lines):
        # _printer( '%3d. %s' %(line_i, line.text.strip()) )
        if line.text.strip() not in proc_tree.keys():
            status = status and False
            _error( 'You are asking me to execute group=`%s`, however I cannot find the defination of this group' %(line.text) )


    if status is False:
        _error( 'Fail!')
        quit()
    # _printer( tcol.OKGREEN+'OK!'+tcol.ENDC )

    X = []
    for line_i, line in enumerate(all_lines):
        _printer( '%3d. %s' %(line_i, line.text.strip()) )
        X.append( proc_tree[line.text.strip() ] )

    #
    # Check repeat in execution
    try:
        rt = execution_tag.attrib['repeat']
    except:
        return X, None


    try:
        repeat_count = execution_tag.attrib['times']
        if _isnum( repeat_count ):
            repeat_count = float(repeat_count)
        else:
            repeat_count = -1
    except:
        repeat_count = -1 # Infinite times

    rt = rt.split('.')
    time_set = ['days', 'weeks', 'months', 'year', 'seconds', 'minutes', 'hours']
    assert( len(rt) == 2 )
    assert( _isnum(rt[0].strip()) )
    assert( rt[1].strip() in time_set )

    if rt[1].strip() == 'days':
        rt_sec = timedelta( days=float(rt[0]) ).total_seconds()
    if rt[1].strip() == 'weeks':
        rt_sec = timedelta( weeks=float(rt[0]) ).total_seconds()
    if rt[1].strip() == 'months':
        rt_sec = timedelta( months=float(rt[0]) ).total_seconds()
    if rt[1].strip() == 'years':
        rt_sec = timedelta( year=float(rt[0]) ).total_seconds()

    if rt[1].strip() == 'seconds':
        rt_sec = timedelta( seconds=float(rt[0]) ).total_seconds()
        if rt[1].strip() == 'minutes':
            rt_sec = timedelta( hours=float(rt[0]) ).total_seconds()
    if rt[1].strip() == 'hours':
        rt_sec = timedelta( hours=float(rt[0]) ).total_seconds()

    _printer( tcol.HEADER+'Repeat execution every %s, ie. %d seconds' %(' '.join(rt), rt_sec )+tcol.ENDC  )
    _printer( tcol.OKGREEN+'Config file OK!'+tcol.ENDC )
    return X, (rt_sec, repeat_count)






def _proc_print( pid, msg ):
    print '[PID=%5d] %s' %(pid, msg)

def exec_task( cmd, log_dir ):
    global global_logserver
    p = multiprocessing.current_process()
    startT = datetime.now()
    log_file = log_dir+'%s.log' %( str(p.pid) )
    log_server = global_logserver #"localhost:9595"


    _proc_print( p.pid, 'Start at %s' %(str(startT)) )
    _proc_print( p.pid, 'cmd: %s' %(cmd) )
    _proc_print( p.pid, 'log : %s' %(log_file) )



    process = subprocess.Popen( cmd+' --logfile=%s --logserver %s' %(log_file,log_server), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    # process = subprocess.Popen( 'sleep 1s', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

    stdout_queue = Queue.Queue()
    stdout_reader = AsynchronousFileReader( process.stdout, stdout_queue )
    stdout_reader.start()

    stderr_queue = Queue.Queue()
    stderr_reader = AsynchronousFileReader( process.stderr, stderr_queue )
    stderr_reader.start()


    # Check the queues if we received some output (until there is nothing more to get).
    while not stdout_reader.eof() or not stderr_reader.eof():
        # Show what we received from standard output.
        while not stdout_queue.empty():
            line = stdout_queue.get()
            # print line,

        # Show what we received from standard error.
        while not stderr_queue.empty():
            line = stderr_queue.get()
            print line,

        # Sleep a bit before asking the readers again.
        time.sleep(.1)

    # Let's be tidy and join the threads we've started.
    stdout_reader.join()
    stderr_reader.join()

    # Close subprocess' file descriptors.
    process.stdout.close()
    process.stderr.close()
    _proc_print( p.pid, 'Complete on %s' %( str(datetime.now())   ) )



    # fp.write( output )
    # fp.write( '\nProc: %s\nStarted: %s\nEnded: %s\n' %( cmd,  str(startT), str(datetime.now() ) ) )
    # fp.close()





## Main

# Parse cmdline arg
parser = argparse.ArgumentParser()
parser.add_argument( '-f', '--config_file', required=True, help='Specify XML config file' )
parser.add_argument( '-sd', '--store_dir', required=False, default=None, help='Overide the store_dir in config with specified. If not specified, then one specified in config will be used.' )
parser.add_argument( '-i', '--interactive', default=False, action='store_true', help='Ask for confirmation before running' )
parser.add_argument( '--logserver', required=True, help='Specify XML config file' )
args = parser.parse_args()


DEBUG_LEVEL = 0
# fname = 'config/retrive_wsj.config.xml'
# fname = 'config/parse_wsj.config.xml'
# fname = 'config/recent_quotes.config.xml'
fname = args.config_file

_printer( 'Open Config     : %s' %(fname) )
_printer( 'Store directory : %s' %(args.store_dir) )
_printer( 'Log Server      : %s' %(args.logserver) )
global_logserver = args.logserver

X, _repeat_info = consolidated_config_to_cmd( fname, args.store_dir )

repeat_in_sec=0
repeat_count=1
if _repeat_info is not None:
    repeat_in_sec, repeat_count = _repeat_info
_i = 0

print 'Repeat for %d times' %(repeat_count)
# for _i in range( 10 ):
while True:
    _i += 1
    if _i > repeat_count and repeat_count > 0:
        break
    _printer( '\n[Run#%d of %d]' %(_i, repeat_count) )


    startTime_run = time.time()
    for cmd_list, log_dir in X:
        # x: cmd_list, log_dir
        # print log_dir
        jobs = []
        startTime = time.time()
        _printer( tcol.HEADER+'---'+tcol.ENDC )
        for cmd in cmd_list:
            _printer( cmd )
            d = multiprocessing.Process( target=exec_task, args=(cmd, log_dir) )
            jobs.append( d )


        if args.interactive:
            if raw_input( 'Confirm (y/n): ' ) != 'y':
                sys.stderr.write( 'Quit()\n' )
                quit()

        for j in jobs:
            j.start()

        for j in jobs:
            j.join()

        done_in = time.time() - startTime
        _printer( tcol.OKBLUE+'<Line> Done in %4.2fs' %( done_in )+tcol.ENDC )


    run_done_in = time.time() - startTime_run
    sleep_for = repeat_in_sec - run_done_in
    _printer( tcol.OKBLUE+'<Execution> complete in %4.2fs. Sleep for %ds' %(run_done_in, sleep_for)+tcol.ENDC )
    if sleep_for > 0:
        _printer( 'Sleeping....zZzz..'+str(datetime.now()) )
        time.sleep( sleep_for )





quit()

# cmd_list, log_dir = config_to_cmd( fname, args.store_dir )
# #TODO : Also return proc_level list. This will let me put the entire config together.
# # Basically all the <process>...</process> with same proc_level can be executed together.
# # The process with proc_level as `i` can be excecuted only after all the proceses
# # with proc_level in {0,1,...,i-1} are complete
# jobs = []
# for cmd in cmd_list:
#     _printer( cmd )
#     d = multiprocessing.Process( target=exec_task, args=(cmd, log_dir) )
#     jobs.append( d )
#     # d.start()
#
# if raw_input( 'Confirm (y/n): ' ) != 'y':
#     sys.stderr.write( 'Quit()\n' )
#     quit()
#
# for j in jobs:
#     j.start()
#
# for j in jobs:
#     j.join()
