from pymongo import MongoClient
import code
import json
import pymongo
from datetime import datetime

## This class shall return information as strings/arrays/lists,tuples etc.
## to it's caller. This will be base class for queries. Might add more classes later
class MongoQueries:
    def __init__( self, client ):
        self.db = client.universalData.universalData # Data of WSJ
        self.quote_db = client.sun_dance.stock_quotes

    ## Returns name of company as string given its ticker. If not found returns None
    def getCompanyName( self, ticker ):
        p = self.db.find_one( {'ticker':'%s' %(ticker), 'type1':'Profile', 'type2':'companyName'} )
        try:
            return p['value_string']
        except:
            return None

    def getCompanyIndustry( self, ticker ):
        p = self.db.find_one( {'ticker':'%s' %(ticker), 'type1':'Profile', 'type2':'companyName'} )
        try:
            return p['industry']
        except:
            return None

    def getCompanySector( self, ticker ):
        p = self.db.find_one( {'ticker':'%s' %(ticker), 'type1':'Profile', 'type2':'companyName'} )
        try:
            return p['sector']
        except:
            return None

    def getCompanyDescription( self, ticker ):
        p = self.db.find_one( {'ticker':'%s' %(ticker), 'type1':'Profile', 'type2':'Description'} )
        try:
            return p['value_string']
        except:
            return None

    def getTickerName( self, ticker ):
        return self.getCompanyName( ticker )
    def getTickerIndustry( self, ticker ):
        return self.getCompanyIndustry( ticker )
    def getTickerSector( self, ticker ):
        return self.getCompanySector( ticker )
    def getTickerDescription( self, ticker ):
        return self.getCompanyDescription( ticker )

        # More timeless info on the company
    def getTickerEmployeesNumber( self, ticker ):
        p = self.db.find_one( {'ticker':'%s' %(ticker), 'type1':'Profile', 'type2':'Company Info', 'type3':'Employees'} )
        try:
            return p['val']
        except:
            return None

    def getTickerStreetAddress( self, ticker ):
        p = self.db.find_one( {'ticker':'%s' %(ticker), 'type1':'Profile', 'type2':'Contact Address'} )
        try:
            return p['value_string']
        except:
            return None


    ## Returns list of industry as string array
    def getIndustryList(self, bourse='HK'):
        query_pipe = [{'$match':{'type1':'Profile', 'type2':'companyName', 'bourse':'%s'%(bourse)}},{'$group': {'_id':'$industry'}} ]
        result=self.db.aggregate( pipeline=query_pipe  )
        to_return = []
        for p in result:
            to_return.append( p['_id'] )

        return to_return

    ## Given an industry string, find its sectors. returns an array of strings
    def getSectorsOf( self, industryName, bourse='HK' ):
        query_pipe = [ {'$match':{'industry':'%s' %(industryName), 'type1':'Profile', 'type2':'companyName', 'bourse':'%s'%(bourse)}},{'$group': {'_id':'$sector'}}  ]
        result=self.db.aggregate( pipeline=query_pipe  )
        to_return = []
        for p in result:
            to_return.append( p['_id'] )

        return to_return

    ## Returns a dictionary like {'2333.HK' : 'Great Wall', '0175.HK': 'Geely'} etc. List
    ## of company in this (industry,sector)
    def getCompanyName_FilterByIndustrynSector( self, industry=None, sector=None, bourse='HK' ):
        #query =  {'type1':'Profile', 'type2':'companyName', 'bourse':'%s'%(bourse), 'industry':'%s' %(industry), 'sector':'%s' %(sector)}
        #query =  {'type1':'Profile', 'type2':'companyName', 'bourse':'%s'%(bourse)}
        query =  {'type1':'Profile', 'type2':'companyName'}

        #TODO Current bourse can only be 1 exchange. Implement bourse to be a comma separated list
        # and correspondingly do a or query if multiple items.
        if bourse is not None:
            query['bourse'] = bourse

        if industry is not None:
            query['industry'] = industry

        if sector is not None:
            query['sector'] = sector

        result=self.db.find( query  )
        to_return = {}
        for p in result:
            to_return[ p['ticker'] ] = p['value_string']

        return to_return

    def getCompanyRevenue( self, industry=None, sector=None, year=None, bourse='HK' ):
        # query = {'type1':'Profile', 'type2':'Company Info', 'type3':'Sales or Revenue', 'bourse':'%s' %(bourse), 'industry':'%s' %(industry), 'sector':'%s' %(sector)}
        query = {}
        # query['type1'] = 'Profile'
        # query['type2'] = 'Company Info'
        # query['type3'] = 'Sales or Revenue'

        query['type1'] = 'Financial Statements'
        query['type2'] = 'income_statement'
        query['period'] = 'a'

        if year is not None:
            query['type4'] = year
        query['type5'] = 'Sales/Revenue'
        query['type6'] = 'None'
        query['type7'] = 'None'


        query['bourse'] = bourse
        if industry is not None:
            query['industry'] = industry
        if sector is not None:
            query['sector'] = sector


        result=self.db.find( query  )
        to_return = []
        for p in result:

            mapTmp = {}
            mapTmp['ticker'] = p['ticker']
            mapTmp['company'] = p['company']
            if 'val' in p:
                mapTmp['revenue'] = float(p['val']) * float(p['fiscal_mul'])
            else:
                mapTmp['revenue'] = 0.0


            to_return.append( mapTmp )

        return to_return

    def getTickerIncomeStatementDetails( self, ticker, year, item_string ):
        #db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements', 'type2':'income_statement', 'type3':'None', 'type4':2016, 'type5':'Sales/Revenue', 'type6':'None', 'type7':'None' } )
        query = {}

        query['ticker'] = ticker
        query['type1'] = 'Financial Statements'
        query['type2'] = 'income_statement'
        # query['period'] = 'a'

        if year is not None:
            query['type4'] = year
        query['type5'] = item_string#'Sales/Revenue'
        query['type6'] = 'None'
        query['type7'] = 'None'

        result=self.db.find_one( query  )

        if result is not None:
            # return result['val']
            return float(result['val']) * float(result['fiscal_mul'])
        else:
            return 0

    def getTickerBalanceSheetAssetsDetails( self, ticker, year, item_string='None', item_string2='None', item_string3='None' ):
        #db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements', 'type2':'balance_sheet', 'type3':'assets', 'type4':2016, 'type5':'Total Accounts Receivable', 'type6':'None', 'type7':'None'} )
        #db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements',
        #'type2':'balance_sheet', 'type3':'assets', 'type4':2016,
        #'type5':'Total Accounts Receivable', 'type6':'None', 'type7':'None'} )

        query = {}

        query['ticker'] = str(ticker)
        query['type1'] = 'Financial Statements'
        query['type2'] = 'balance_sheet'
        query['type3'] = 'assets'
        # query['period'] = 'a'

        if year is not None:
            query['type4'] = year

        query['type5'] = item_string#'Total Assets'
        query['type6'] = item_string2#'None'
        query['type7'] = item_string3#'None'

        # return str(query)
        result=self.db.find_one( query  )


        if result is not None:
            return float(result['val']) * float(result['fiscal_mul'])
        else:
            return 'N/A'


    def getTickerBalanceSheetLiabilitiesDetails( self, ticker, year, item_string='None', item_string2='None', item_string3='None' ):
        #db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements', 'type2':'balance_sheet', 'type3':'assets', 'type4':2016, 'type5':'Total Accounts Receivable', 'type6':'None', 'type7':'None'} )
        #db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements',
        #'type2':'balance_sheet', 'type3':'assets', 'type4':2016,
        #'type5':'Total Accounts Receivable', 'type6':'None', 'type7':'None'} )

        query = {}

        query['ticker'] = str(ticker)
        query['type1'] = 'Financial Statements'
        query['type2'] = 'balance_sheet'
        query['type3'] = 'liabilities'
        # query['period'] = 'a'

        if year is not None:
            query['type4'] = year

        if item_string != 'None':
            query['type5'] = item_string#'Total Assets'

        query['type6'] = item_string2#'None'
        query['type7'] = item_string3#'None'
        # return str(query)

        result=self.db.find_one( query  )

        if result is not None:
            return float(result['val']) * float(result['fiscal_mul'])
        else:
            return 'N/A'


    #TODO implement getCashFlowOperatingActivityDetails, getCashFlowInvestingActivityDetails, getCashFlowFinancingActivityDetails
    def getCashFlowOperatingActivityDetails( self, ticker, year, item_string='None', item_string2='None', item_string3='None' ):
        #db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements', 'type2':'cash_flow_statement', 'type3':'operating', 'type4':2016, 'type5':'Other Funds', 'type6':'None', 'type7':'None'})
        #db.getCollection('universalData').find({'ticker':'2333.HK',
        #   'type1':'Financial Statements', 'type2':'cash_flow_statement',
        #   'type3':'operating', 'type4':2016,
        #   'type5':'Other Funds', 'type6':'None', 'type7':'None'})
        query = {}

        query['ticker'] = str(ticker)
        query['type1'] = 'Financial Statements'
        query['type2'] = 'cash_flow_statement'
        query['type3'] = 'operating'
        # query['period'] = 'a'

        if year is not None:
            query['type4'] = year

        if item_string != 'None':
            query['type5'] = item_string#'Total Assets'

        query['type6'] = item_string2#'None'
        query['type7'] = item_string3#'None'
        # return str(query)

        result=self.db.find_one( query  )

        if result is not None:
            return float(result['val']) * float(result['fiscal_mul'])
        else:
            return 'N/A'


    def getCashFlowInvestingActivityDetails( self, ticker, year, item_string='None', item_string2='None', item_string3='None' ):
        #db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements', 'type2':'cash_flow_statement', 'type3':'operating', 'type4':2016, 'type5':'Other Funds', 'type6':'None', 'type7':'None'})
        #db.getCollection('universalData').find({'ticker':'2333.HK',
        #   'type1':'Financial Statements', 'type2':'cash_flow_statement',
        #   'type3':'operating', 'type4':2016,
        #   'type5':'Other Funds', 'type6':'None', 'type7':'None'})
        query = {}

        query['ticker'] = str(ticker)
        query['type1'] = 'Financial Statements'
        query['type2'] = 'cash_flow_statement'
        query['type3'] = 'investing'
        # query['period'] = 'a'

        if year is not None:
            query['type4'] = year

        if item_string != 'None':
            query['type5'] = item_string#'Total Assets'

        query['type6'] = item_string2#'None'
        query['type7'] = item_string3#'None'
        # return str(query)

        result=self.db.find_one( query  )

        if result is not None:
            return float(result['val']) * float(result['fiscal_mul'])
        else:
            return 'N/A'


    def getCashFlowFinancingActivityDetails( self, ticker, year, item_string='None', item_string2='None', item_string3='None' ):
        #db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements', 'type2':'cash_flow_statement', 'type3':'operating', 'type4':2016, 'type5':'Other Funds', 'type6':'None', 'type7':'None'})
        #db.getCollection('universalData').find({'ticker':'2333.HK',
        #   'type1':'Financial Statements', 'type2':'cash_flow_statement',
        #   'type3':'operating', 'type4':2016,
        #   'type5':'Other Funds', 'type6':'None', 'type7':'None'})
        query = {}

        query['ticker'] = str(ticker)
        query['type1'] = 'Financial Statements'
        query['type2'] = 'cash_flow_statement'
        query['type3'] = 'financing'
        # query['period'] = 'a'

        if year is not None:
            query['type4'] = year

        if item_string != 'None':
            query['type5'] = item_string#'Total Assets'

        query['type6'] = item_string2#'None'
        query['type7'] = item_string3#'None'
        # return str(query)

        result=self.db.find_one( query  )

        if result is not None:
            return float(result['val']) * float(result['fiscal_mul'])
        else:
            return 'N/A'



    def getTickerDailyQuote( self, ticker, date, field=None ):
        if field not in ['close', 'close_adj', 'volume', 'datetime', 'inserted_on', 'open', 'high', 'low']:
            return "ERROR2"

        query = {}
        query['ticker'] = ticker
        if date == None:
            # db.getCollection('stock_quotes').find({'ticker':'2208.HK'}).sort( {'datetime':-1, 'inserted_on':-1} ).limit(1)
            pass
        else:
            # return str(datetime.strptime( date, '%Y-%m-%d' ))
            # Allowed dates: a) 20170705 b) 2017-07-05 c) 2017-Jul-5 d) 2017-July-05
            try:
                query['datetime'] = datetime.strptime( date, '%Y%m%d' )
            except ValueError:
                try:
                    query['datetime'] = datetime.strptime( date, '%Y-%m-%d' )
                except:
                    try:
                        query['datetime'] = datetime.strptime( date, '%Y-%b-%d' )
                    except:
                        try:
                            query['datetime'] = datetime.strptime( date, '%Y-%B-%d' )
                        except:
                            return "query failed. invalid date"
            # return str(query)

        # Will return the latest inserted data.
        result = self.quote_db.find( query ).sort( [('datetime',pymongo.DESCENDING), ('inserted_on',pymongo.DESCENDING)] ).limit(1)

        if result is not None:
            # print result
            for r in result:
                return str(r[field])#+','+str(r['datetime'])
            else:
                return "N/A"
        else:
            return "query fail"
