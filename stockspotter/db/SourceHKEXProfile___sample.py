""" Processor for HKEX profile
        Sample : http://www.hkex.com.hk/eng/invest/company/profile_page_e.asp?WidCoID=0341

        This class will provide function a) download from url, b) load from file if exist
        c) process the dump d) many many getter functions

"""
import sys
import os.path
import urllib2

from bs4 import BeautifulSoup
import pickle

import TerminalColors
tcol = TerminalColors.bcolors()

class SourceHKEXProfile:
    def __init__(self, ticker, stock_prefix):
        """ ticker : Stock ticker eg. 2333.HK
        stock_prefix : Storage directory eg. eq_db/data_2016_Dec_09/0175.HK/
        """

        print 'constructor'
        self.ticker = ticker
        self.stock_prefix = stock_prefix

    def load_url(self):
        """ Having known the ticker and stock_prefix, download the files into the folder """
        # mkdir a folder within the stock_prefix (if not exits)


        # Setup the url

        # write file

    def load_file(self):
        x=0
