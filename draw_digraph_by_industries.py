""" Lists .pk1 files and makes a industry di-graph of it """

import sys
import time
import os.path
import urllib2

from bs4 import BeautifulSoup
from yahoo_finance import Share

import pickle
import glob
import re

from anytree import Node, RenderTree # Tree data structure
from anytree.dotexport import RenderTreeGraph


def load_obj( name ):
    """ Load pickle file and return data_dict """
    with open( name, 'rb' ) as f:
        return pickle.load(f)


def clean_industry_path( the_string ):
    industry = re.sub( ' +', ' ', str(the_string.replace('\xc2\xa0','').replace('\r','').replace('\t','').strip()) )
    industry = industry.split( " - " )
    return industry

def clean_string( the_string ):
    return re.sub( ' +', ' ', str(the_string.replace('\xc2\xa0','').replace('\r','').replace('\t','').strip()) )


def find_in_node_list( children_list, to_find ):
    """ Given a list of nodes, find the node named `to_find` """
    for i in children_list:
        if i.name == str(to_find):
            return i

    return None


def get_node_ptr( root, industry ):
    """ Given the industry-tree root, returns the pointers of the industry[]. This assumes a complete tree. might fail if tree is incomplete """

    ptr_list = []

    a = find_in_node_list( root.children, industry[0] )
    b = find_in_node_list( a.children, industry[1] )
    ptr_list.append(a)
    ptr_list.append(b)

    if len(industry) > 2:
        c = find_in_node_list( b.children, industry[2])
        ptr_list.append(c)
    else:
        c = None

    return ptr_list


def build_industry_tree( list_pk ):
    """ Given a list of .pk files (pickle), builds an industry tree using anytree py-package """

    # Build tree
    print 'Build Industry-Tree'
    startTime = time.time()
    root = Node( 'root' )
    for pickle_fname in list_pk:
        # print pickle_fname

        # Load pickle file for stock
        data_dict = load_obj( pickle_fname )
        industry = clean_industry_path( str(data_dict['Industry Classification']) )

        # if len(industry) != 3:
        #     print industry


        # Look at industry classification in data_dict and create the tree
        m = find_in_node_list(root.children, industry[0])
        if  m == None:
            m = Node( industry[0], parent=root )
        else:
            n = find_in_node_list( m.children, industry[1])
            if n == None:
                n = Node( industry[1], parent=m )
            else:
                if len(industry) > 2 :
                    p = find_in_node_list( n.children, industry[2] )
                    if p == None:
                        p = Node( industry[2], parent=n )
    print 'Finished Building Industry-Tree in ', time.time() - startTime, ' sec'
    return root


def populate_tickers_to_industry_tree( root, list_pk ):
    """ Populate company tickers as leaf nodes """

    print 'Add tickers as Industry-Tree leafs'
    startTime = time.time()
    for pickle_fname in list_pk:
        # Load pickle file for stock
        data_dict = load_obj( pickle_fname )
        industry = clean_industry_path( str(data_dict['Industry Classification']) )


        # Given the industry[] return all the nodes. size of node-list should equal the size of industry[]
        ptr_list = get_node_ptr( root, industry )

        ticker = data_dict['ticker'][0:7] #clean_string(data_dict['ticker'])

        co_name = clean_string( data_dict['Company/Securities Name'] )
        # print ticker
        Node( 'ticker_'+ticker+'_'+co_name, parent=ptr_list[-1] )

    print 'Finished adding tickers in', time.time() - startTime, ' sec'




list_pk = glob.glob( 'equities_data/*.hkex_profile.pk1' )
# PASS-1 : Builds basic industry tree
root = build_industry_tree( list_pk )




# PASS-2 : Populate company tickers as leaf nodes
populate_tickers_to_industry_tree( root, list_pk )








# print(RenderTree(root.children[1].children[1]))
# RenderTreeGraph(root.children[0]).to_picture("industry.png")


# for p in root.children[0].children: print p.name
