
import sys
import os.path
import urllib2
import pprint


from TickerLister import TickerLister


lister = TickerLister()
tmp = lister.list_full_hkex()
