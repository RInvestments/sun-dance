""" Test script for subprocess downloader """

from lxml import etree

def _error( msg ):
    print '[ERROR] ', msg

def _debug( msg ):
    print '[DEBUG] ', msg


def config_to_cmd( fname ):
    self._debug( 'Open XML config : %s' %(fname) )

    doc = etree.parse( fname )
    global_ele = doc.find( 'global' )

    # Iterate over each process
    for p in doc.findall( 'process' ):
        print '---'
        # print p.find( 'type' ).text
        # print p.find( 'source' ).text
        # print p.find( 'exchange' ).text
        # print p.find( 'verbosity' ).text

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


            print 'python data_retriver.py -sd %s -ld %s %s %s -v %d' %(store_dir, list_db, task_arg, exchange_arg, verbosity )



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


            print 'python data_parser.py -sd %s -ld %s %s %s -v %d' %(store_dir, list_db, task_arg, exchange_arg, verbosity )



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


            print 'python data_inserter.py -sd %s -ld %s %s %s -v %d' %(store_dir, list_db, task_arg, exchange_arg, verbosity )


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


            print 'python daily_quote_inserter.py -sd %s -ld %s %s -v %d' %(store_dir, list_db, exchange_arg, verbosity )


fname = 'config/simple.config.xml'
cmd_list = config_to_cmd( fname )
