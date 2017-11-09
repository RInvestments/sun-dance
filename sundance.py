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
import sys

import threading
import Queue

def _error( msg ):
    print '[ERROR] ', msg

def _debug( msg, lvl=1 ):
    if lvl in range( DEBUG_LEVEL ):
        print '[DEBUG=%d] ' %(lvl), msg

def _printer( msg ):
    print msg

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


def config_to_cmd( fname ):
    _debug( 'Open XML config : %s' %(fname) )

    doc = etree.parse( fname )
    global_ele = doc.find( 'global' )

    # Iterate over each process
    cmd_list = []
    for p in doc.findall( 'process' ):
        # _debug( '---', 2 )

        if p.find( 'type' ).text.strip() == 'retriver':

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


            cmd = 'python data_inserter.py -sd %s -ld %s %s %s -v %d' %(store_dir, list_db, task_arg, exchange_arg, verbosity )
            _debug( cmd, 2)
            cmd_list.append( cmd )


        if p.find( 'type' ).text.strip() == 'quote_inserter':
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


            cmd = 'python daily_quote_inserter.py -sd %s -ld %s %s -v %d' %(store_dir, list_db, exchange_arg, verbosity )
            _debug( cmd, 2 )
            cmd_list.append( cmd )



    # Log dir
    try:
        log_dir = global_ele.find( 'log_dir' ).text.strip()
    except:
        try:
            log_dir = global_ele.find( 'store_dir' ).text.strip()
        except:
            log_dir = '/tmp/'
    return cmd_list, log_dir


def _proc_print( pid, msg ):
    print '[PID=%5d] %s' %(pid, msg)

def exec_task( cmd, log_dir ):
    p = multiprocessing.current_process()
    startT = datetime.now()
    log_file = log_dir+'/%s.log' %(p.pid)


    _proc_print( p.pid, 'Start at %s' %(str(startT)) )
    _proc_print( p.pid, 'cmd: %s' %(cmd) )
    _proc_print( p.pid, 'log : %s' %(log_file) )



    process = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

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
            print line,

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
    _proc_print( p.pid, 'Complete!' )



    # fp.write( output )
    # fp.write( '\nProc: %s\nStarted: %s\nEnded: %s\n' %( cmd,  str(startT), str(datetime.now() ) ) )
    # fp.close()





## Main

# Parse cmdline arg
parser = argparse.ArgumentParser()
parser.add_argument( '-f', '--config_file', required=True, help='Specify XML config file' )
args = parser.parse_args()


DEBUG_LEVEL = 0
# fname = 'config/retrive_wsj.config.xml'
# fname = 'config/parse_wsj.config.xml'
# fname = 'config/recent_quotes.config.xml'
fname = args.config_file

_printer( 'Open Config : %s' %(fname) )
cmd_list, log_dir = config_to_cmd( fname )

jobs = []
for cmd in cmd_list:
    _printer( cmd )
    d = multiprocessing.Process( target=exec_task, args=(cmd, log_dir) )
    jobs.append( d )
    # d.start()

if raw_input( 'Confirm (y/n): ' ) != 'y':
    sys.stderr.write( 'Quit()\n' )
    quit()

for j in jobs:
    j.start()

for j in jobs:
    j.join()
