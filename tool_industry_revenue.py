""" Tool to visualize industry by revenue.
    Inspired from https://www.youtube.com/watch?v=5Zg-C8AAIGg

    Author  : Manohar Kuse <mpkuse@connect.ust.hk>
    Created : 12th Apr, 2017
"""

from pymongo import MongoClient
import pprint

from bokeh.plotting import figure, output_file, show, save
import numpy as np

import matplotlib.pyplot as plt

client = MongoClient()

db = client.universalData.universalData
pprint.pprint( db.find_one({'ticker':'0011.HK', 'type1':'Profile', 'type2':'Company Info', 'type3':'Sales or Revenue' }) )

#cursor = db.find({'industry':'Automotive', 'sector':'Auto & Commercial Vehicle Parts', 'type1':'Profile', 'type2':'Company Info', 'type3':'Sales or Revenue' }, \
#                    {'industry':1, 'sector':1, 'company':1, 'ticker':1, 'val':1} )

year = 2012

for year in [2012,2013,2014,2015]:
    cursor = db.find({'industry':'Automotive', 'sector':'Automobiles', 'type1':'Financial Statements', 'type2':'income_statement', 'type3':'None', 'period':'a', 'type5':'Sales/Revenue', 'type6':'None',  'type7':'None', 'type4':year }, \
                        {'industry':1, 'sector':1, 'company':1, 'ticker':1, 'val':1} ).sort( 'company', 1 )


    revenue = []
    labels = []
    for json_rev in cursor:
        pprint.pprint( json_rev )

        try:
            v = json_rev['val']
        except KeyError:
            v = 0
        revenue.append( v )
        labels.append( json_rev['company'] )
    pdf = np.array(revenue)/sum(revenue)
    cdf = np.cumsum( pdf )

    plt.clf()
    plt.pie( pdf*100, autopct='%1.1f%%', shadow=True, labels=labels )
    plt.axis( 'equal')
    plt.show(False)
    plt.pause(1)
