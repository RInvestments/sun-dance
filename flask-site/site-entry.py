from flask import Flask
from flask import render_template
from pymongo import MongoClient
import numpy as np
from MongoQueries import MongoQueries
import pprint
import json

# MongoDB
client = MongoClient()
db = client.universalData.universalData
ave = MongoQueries(db)

# Flask
app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return "Opps! Page cannot be found - 404"

@app.route("/")
def hello():
    return "Hello World!"

@app.route( "/test/<name>")
def template_hello(name):
    return render_template( 'hello.html', name=name )



#------------------------ API Calls ---------------------------#


#### Ticker Info Calls
@app.route( '/api/info/<ticker>')
def lookup_ticker( ticker ):
    return ave.getCompanyName( ticker )

@app.route( '/api/info/<ticker>/is/<datum>/<int:year>' ) #income statement data
def lookup_ticker_income_statement( ticker, datum, year ):
    alias = {}
    alias['revenue' ] = "Sales/Revenue"
    alias['cogs' ] = "Cost of Goods Sold (COGS) incl. D&A"
    alias['income_gross' ] = "Gross Income"
    alias['income_pretax' ] = "Pretax Income"
    alias['income_net' ] = "Net Income"
    alias['expense_sga' ] = "SG&A Expense"
    alias['expense_interest' ] = "Interest Expense"
    alias['expense_tax' ] = "Income Tax"
    alias['ebit' ] = "EBIT"
    alias['ebitda' ] = "EBITDA"
    alias['eps' ] = "EPS (Diluted)"
    alias['eps_basic' ] = "EPS (Basic)"
    alias['eps_diluted' ] = "EPS (Diluted)"
    alias['shares_outstanding' ] = "Diluted Shares Outstanding"

    if datum in alias.keys():
        return str(ave.getTickerIncomeStatementDetails( ticker, year, alias[datum] ))
    else:
        if datum == '_list_':
            return str( alias.keys() )
        if datum == '_list_col_':
            s = ""
            for k in alias.keys():
                s += k+ '\n'
            return s
        if datum == '_json_':
            return json.dumps( alias )
        return "#N/A %s" %(datum)


@app.route( '/api/info/<ticker>/bs/<datum>/<int:year>' ) #income statement data
def lookup_ticker_balance_sheet( ticker, datum, year ):
    alias_assets = {}
    alias_assets['']
    return str(ave.getTickerBalanceSheetAssetsDetails( ticker, year, "Net Property, Plant & Equipment", "Accumulated Depreciation", "Construction in Progress" ))
    # return str(ave.getTickerBalanceSheetLiabilitiesDetails( ticker, year, 'None', "Quick Ratio" ))




#### List calls
@app.route( '/api/list/industry_list')
def lookup_industry_list( ):
    list_of_industry = ave.getIndustryList()
    s=''
    for l in sorted(list_of_industry):
        s += l+','
    return s[:-1].replace( '/', '_')


@app.route( '/api/list/<industry>/sector_list')
def lookup_sector_list( industry ):
    industry = industry.replace( '_', '/' )
    list_of_sectors = ave.getSectorsOf( industryName=industry )
    s=''
    for sector in sorted(list_of_sectors):
        s += sector+','
    return s[:-1].replace( '/', '_')

@app.route( '/api/list/<industry>/<sector>/company_list')
def lookup_company_list( industry, sector ):
    industry = industry.replace( '_', '/' )
    sector = sector.replace( '_', '/' )

    if industry == 'None':
        industry = None
    if sector == 'None':
        sector = None

    list_of_companies = ave.getCompanyName_FilterByIndustrynSector( industry=industry, sector=sector )
    s = ''
    for ticker in list_of_companies.keys():
        s += ticker+','
    return s[:-1]



#----------------------- END API ------------------------------#



#----------------------- Company Info -------------------------#

@app.route( '/companyInfo/<ticker>/name')
def show_name( ticker ):
    # return ticker
    return ave.getCompanyName( ticker ) + "<p>" + ave.getCompanyDescription(ticker) + '</p>'


@app.route( '/companyInfo/<ticker>/income_statement/<int:year>')
def show_income_statement_analysis( ticker, year ):
    revenue = ave.getTickerIncomeStatementDetails( ticker, year, 'Sales/Revenue' )
    cogs = ave.getTickerIncomeStatementDetails( ticker, year, 'Cost of Goods Sold (COGS) incl. D&A' )
    sga = ave.getTickerIncomeStatementDetails( ticker, year, 'SG&A Expense' )
    income_tax = ave.getTickerIncomeStatementDetails( ticker, year, 'Income Tax' )
    net_income = ave.getTickerIncomeStatementDetails( ticker, year, 'Net Income Available to Common' )
    interest_exp = revenue - cogs - sga - income_tax - net_income

    income_statement = []
    income_statement.append( {'type': 'Cost of Goods Sold', 'value': cogs } )
    income_statement.append( {'type': 'Selling, General and Administrative Expenses', 'value': sga } )
    income_statement.append( {'type': 'Income Tax', 'value': income_tax } )
    income_statement.append( {'type': 'Interest Expense', 'value': interest_exp } )
    # return str(json.dumps(income_statement) )
    return render_template( 'beautifulTable.html', INFO=income_statement, pie=json.dumps( income_statement ), pie_titleField='type', pie_valueField='value'   )



#-------------------- Industry -------------------------------#
@app.route( '/industryInfo/list')
def show_industry_list():
    list_of_industry = ave.getIndustryList()
    s='<h2>List of Industry</h2>'
    for l in sorted(list_of_industry):
        s += l+'<br/>'
    return s

@app.route( '/industryInfo/collapsibleList')
def show_collapsible_list():
    INFO = {}
    for industry in sorted( ave.getIndustryList() ):
        INFO[industry] = {}
        for sector in sorted(ave.getSectorsOf( industry )):
            INFO[industry][sector] = ave.getCompanyName_FilterByIndustrynSector( industry, sector, bourse='HK' )

    return render_template( 'collapsible.html', INFO=INFO )


@app.route( '/industryInfo/<industry>/list')
def show_sector_list(industry):
    list_of_sectors = ave.getSectorsOf( industryName=industry )
    s='<h2>List of Sectors of :  %s</h2>' %(industry)
    for sector in sorted(list_of_sectors):
        s += sector+'<br/>'
    return s

@app.route( '/industryInfo/<industry>/revenue/<int:year>')
def show_industry_revenue(industry, year):
    industry = industry.replace( "_", "/")
    list_of_revenue = ave.getCompanyRevenue(industry=industry, year=year, bourse='HK')
    return render_template( 'beautifulTable.html', INFO=list_of_revenue, pie=json.dumps( list_of_revenue ), pie_valueField='revenue', pie_titleField='company'  )


@app.route( '/industryInfo/<industry>/interest_expense/<int:year>')
def show_industry_interest_exp( industry, year ):
    industry = industry.replace( "_", "/")


    list_of_companies = ave.getCompanyName_FilterByIndustrynSector( industry=industry)
    INFO = []
    for ticker in list_of_companies:
        R = {}
        R['ticker'] = ticker
        R['name'] = list_of_companies[ticker]
        R['Industry'] = industry
        R['Sector'] = ave.getCompanySector( ticker )


        revenue = ave.getTickerIncomeStatementDetails( str(ticker), year, 'Sales/Revenue' )
        cogs = ave.getTickerIncomeStatementDetails( ticker, year, 'Cost of Goods Sold (COGS) incl. D&A' )
        sga = ave.getTickerIncomeStatementDetails( ticker, year, 'SG&A Expense' )
        income_tax = ave.getTickerIncomeStatementDetails( ticker, year, 'Income Tax' )
        net_income = ave.getTickerIncomeStatementDetails( ticker, year, 'Net Income Available to Common' )
        interest_exp = revenue - cogs - sga - income_tax - net_income
        if revenue != 0:
            R['Interest Expense(As percentage of revenue)'] = np.round(interest_exp/revenue,4) * 100
        else:
            R['Interest Expense(As percentage of revenue)'] = 0

        INFO.append( R )
    return render_template( 'cleanTable.html', INFO=INFO )


#-----------------Industry and Sector --------------------#

@app.route( '/industryInfo/<industry>/<sector>/revenue/<int:year>')
def show_industry_sector_revenue(industry, sector, year):
    industry = industry.replace( "_", "/")
    sector = sector.replace( "_", "/")
    list_of_revenue = ave.getCompanyRevenue(industry=industry, sector=sector, year=year, bourse='HK')
    return render_template( 'beautifulTable.html', INFO=list_of_revenue, pie=json.dumps( list_of_revenue ), pie_valueField='revenue', pie_titleField='company'  )



@app.route( '/industryInfo/<industry>/<sector>/list')
def show_companies( industry, sector ):
    list_of_companies = ave.getCompanyName_FilterByIndustrynSector( industry=industry, sector=sector )
    s = '<h2>Showing companies within industry:"%s" and sector:"%s"</h2>' %(industry, sector)
    for ticker in list_of_companies:
        s+= '%s %s</br>' %(ticker, list_of_companies[ticker])
    return s


@app.route( '/industryInfo/<industry>/<sector>/interest_expense/<int:year>')
def show_industry_sector_interest_exp( industry, sector, year ):
    industry = industry.replace( "_", "/")
    sector = sector.replace( "_", "/")

    list_of_companies = ave.getCompanyName_FilterByIndustrynSector( industry=industry, sector=sector )
    INFO = []
    for ticker in list_of_companies:
        R = {}
        R['ticker'] = ticker
        R['name'] = list_of_companies[ticker]
        R['Industry'] = industry
        R['Sector'] = sector

        revenue = ave.getTickerIncomeStatementDetails( str(ticker), year, 'Sales/Revenue' )
        cogs = ave.getTickerIncomeStatementDetails( ticker, year, 'Cost of Goods Sold (COGS) incl. D&A' )
        sga = ave.getTickerIncomeStatementDetails( ticker, year, 'SG&A Expense' )
        income_tax = ave.getTickerIncomeStatementDetails( ticker, year, 'Income Tax' )
        net_income = ave.getTickerIncomeStatementDetails( ticker, year, 'Net Income Available to Common' )
        interest_exp = revenue - cogs - sga - income_tax - net_income
        if revenue != 0:
            R['Interest Expense(As percentage of revenue)'] = np.round(interest_exp/revenue,4) * 100
        else:
            R['Interest Expense(As percentage of revenue)'] = 0

        INFO.append( R )
    return render_template( 'cleanTable.html', INFO=INFO )




if __name__ == "__main__":
    app.run()
