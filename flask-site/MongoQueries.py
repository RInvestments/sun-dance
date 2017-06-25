from pymongo import MongoClient
import code

## This class shall return information as strings/arrays/lists,tuples etc.
## to it's caller. This will be base class for queries. Might add more classes later
class MongoQueries:
    def __init__( self, db ):
        self.db = db

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
