""" Processor class for Hang Seng Indices
        Functions to retrive the constituents of HSI group of indices. Managing
        the storage. Also functions to give out requested HSI

        The data has been downloaded from datafeeds of official hsi.com.hk

        Author  : Manohar Kuse <mpkuse@connect.ust.hk>
        Created : 18th Mar, 2017
"""
import sys
import os
import urllib2
import time
import code
import string
import code
import collections

import json
import defusedxml.ElementTree as et

from TickerPoint import TickerPoint


import TerminalColors
tcol = TerminalColors.bcolors()
tcolor = tcol


class HSILister:
    def __init__(self, lists_db, verbosity=0):
        self.verbosity = range(verbosity)

        self.lists_db = lists_db
        self.priv_dir = lists_db+'/hsi-net/'
        self._debug( 'Set priv directory : '+self.priv_dir )
        self._make_folder_if_not_exist( self.priv_dir )


    #################### Printer functions ################
    def _printer( self, txt ):
        print tcol.OKBLUE, 'TickerLister :', tcol.ENDC, txt

    def _debug( self, txt, lvl=0 ):
        """ """
        to_print = self.verbosity
        if lvl in to_print:
            print tcol.OKBLUE, 'TickerLister(Debug=%2d) :' %(lvl), tcol.ENDC, txt

    def _error( self, txt ):
        """ """
        print tcol.FAIL, 'TickerLister(Error) :', tcol.ENDC, txt

    def _report_time( self, txt ):
        print tcol.OKBLUE, 'TickerLister(time) :', tcol.ENDC, txt


    ############# retrival-core #####################
    ## Given an hsi id, will download from the official site the XML content and save
    ## it as is in the `self.priv_dir`+hsi_id.xml. Setting hsi_id as None will download
    ## the entire concatenated file

    def _core_retriver( self, hsi_id=None ):
        #URL example : https://www.hsi.com.hk/HSI-Net/HSI-Net?cmd=nxgenindex&index=0001
        if hsi_id is None:
            core_url = 'https://www.hsi.com.hk/HSI-Net/HSI-Net?cmd=nxgenindex'
        else:
            core_url = 'https://www.hsi.com.hk/HSI-Net/HSI-Net?cmd=nxgenindex&index=%04d' %(hsi_id)

        self._debug( 'Download : %s' %(core_url) )
        xml = urllib2.urlopen(core_url).read()  # List of securities

        if hsi_id is None:
            out_file_name = self.priv_dir+'/all_hsi_indices.xml'
        else:
            out_file_name = self.priv_dir+'/%04d.xml' %(hsi_id)

        self._debug( 'Write to file : '+out_file_name )
        with open(out_file_name, 'w') as fp:
            fp.write( xml )



    ############# download ##################
    def download(self):
        A = {}
        A['1'] = 'HSI, Hang Seng Index'
        A['14'] = 'HSCEI, Hang Seng China Enterprises Index'

        A['15'] = 'HSCCI, Hang Seng China-Affiliated Corporations Index' #Red-chip index
        A['22'] = 'HSHFI, Hang Seng China H-Financials Index'
        A['18'] = 'HSCHK100, Hang Seng China (Hong Kong-listed) 100 Index'
        A['21'] = 'HSCHK25, Hang Seng China (Hong Kong-listed) 25 Index'


        A['2007'] = 'HSMBI, Hang Seng Mainland Banks Index'
        A['2008'] = 'HSMPI, Hang Seng Mainland Properties Index'
        A['2009'] = 'HSMHI, Hang Seng Mainland Healthcare Index'
        A['2010'] = 'HSMOGI, Hang Seng Mainland Oil and Gas Index'
        A['2011'] = 'HSITHI, Hang Seng IT Hardware Index'
        A['2012'] = 'HSSSI, Hang Seng Software and Services Index'

        A['20'] = 'HSHK35, Hang Seng HK 35'
        A['2018'] = 'HSCGSI, Hang Seng Consumer Goods and Services Index'
        A['2017'] = 'HSHCI, Hang Seng Healthcare Index'
        A['2016'] = 'HSIII, Hang Seng Internet and Information Technology Index'

        A['11'] = 'HSCI, Hang Seng Composite Index'
        A['1053'] = 'HSFCCI, Hang Seng Foreign Companies Composite Index'


        startTime = time.time()
        for k in A:
            print k, A[k]
            self._core_retriver( hsi_id = int(k) )
        self._report_time( 'Downloaded XMLs in %4.2fs' %(  (time.time() - startTime)   ) )


    def download_all_index(self):
        """ Downloads the entire index db as 1 file. This is done by setting index=<blank> in the url"""
        startTime = time.time()
        self._core_retriver( )
        self._report_time( 'Downloaded XMLs in %4.2fs' %(  (time.time() - startTime)   ) )


    ############ XML Parsering/Searching #############

    def _get_constituents(self, index):
        """ Given an sub-tree of index, return an array of type TickerPoint of its constituents """
        ticker_list = []
        for c in index.find( 'constituents' ):
            # print c.find( 'name' ).text, c.attrib['hcode']
            stock_name = c.find( 'name' ).text
            stock_ticker = '%04d.HK' %(int(c.attrib['hcode']))
            tmp = TickerPoint( name=stock_name, ticker=stock_ticker)
            ticker_list.append(tmp)
        return ticker_list

    def _print_index_debug( self, index, msg ):
        strr = 'no,code,name : %s,%s,%s' %(index.get('no'), index.get('code'), index.find('name').text )
        n_sub_indx = len(index.find('sub-indexes' ) ) if index.find('sub-indexes' ) is not None else 0
        n_constituents =  len(index.find('constituents' ) )
        strr2 = '# sub-indices : %d ; # constituents : %d' %( n_sub_indx, n_constituents)
        self._debug( msg+strr )
        self._debug( msg+strr, lvl=1 )

    def test_parse_xml(self):
        """ This function is for dry testing """
        tree = et.parse( self.priv_dir+'/all_hsi_indices.xml' )
        root = tree.getroot()

        for index in root:
            if index.get('no') == '00001':
                # print index.tag, index.attrib['no'], index.attrib['code'], index.find('name').text
                # print '# sub-indices : ', len(index.find('sub-indexes' ))
                # print '# constituents : ', len(index.find('constituents' ))
                ticker_list = self._get_constituents( index )
        # code.interact( local=locals() )
        return ticker_list



    def search_by_index_no(self, no ):
        """ Example of index no : 1, 14, 2016 etc """
        tree = et.parse( self.priv_dir+'/all_hsi_indices.xml' )
        root = tree.getroot()
        for index in root:
            if index.get('no') == '%05d' %(no):
                self._print_index_debug( index, 'found `index` in `search_by_index_no()`' )
                ticker_list = self._get_constituents( index )
                return ticker_list
        self._error( 'Cannot find index with no=%05d in %s' %(no, self.priv_dir+'/all_hsi_indices.xml'))
        return []

    def search_by_index_code(self, code ):
        """ Example of index code : HSI, HSSI, HSIII etc """
        tree = et.parse( self.priv_dir+'/all_hsi_indices.xml' )
        root = tree.getroot()
        for index in root:
            if index.get('code') == code:
                self._print_index_debug( index, 'found `index` in `search_by_index_code()`' )
                ticker_list = self._get_constituents( index )
                return ticker_list
        self._error( 'Cannot find index with code=%s in %s' %(code, self.priv_dir+'/all_hsi_indices.xml'))
        return []


    def search_by_index_name( self, name ):
        """ Example of index names : 'Hang Seng Index', 'Hang Seng Internet & Information Technology Index' etc """
        tree = et.parse( self.priv_dir+'/all_hsi_indices.xml' )
        root = tree.getroot()
        for index in root:
            if index.find('name').text.strip() == name.strip():
                self._print_index_debug( index, 'found `index` in `search_by_index_name()`' )
                ticker_list = self._get_constituents( index )
                return ticker_list
        self._error( 'Cannot find index with name=\'%s\' in %s' %(code, self.priv_dir+'/all_hsi_indices.xml'))
        return []



    #TODO: search sub-index (low-priority)


    ########## Other Helpers ##############
    def _make_folder_if_not_exist(self, folder):
        if not os.path.exists(folder):
            self._debug( 'Make Directory : ' + folder )
            os.mkdir(folder)
        else:
            self._debug( 'Directory already exists : Not creating : ' + folder )
