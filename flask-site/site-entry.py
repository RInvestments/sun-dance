from flask import Flask
from flask import render_template
from pymongo import MongoClient
import numpy as np
from MongoQueries import MongoQueries
import pprint
import json
import datetime
from collections import OrderedDict

# MongoDB
client = MongoClient()
db = client.universalData.universalData
ave = MongoQueries(client)

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

@app.route( '/api/info/<ticker>/<datum>')
def lookup_ticker_timeless_info( ticker, datum ):
    f='%s %s' %(ticker, datum)

    alias = {} #list of functions. all functions can be called like f( ticker )
    alias['name'] = ave.getTickerName
    alias['industry'] = ave.getTickerIndustry
    alias['sector'] = ave.getTickerSector
    alias['desc'] = ave.getTickerDescription
    alias['description'] = ave.getTickerDescription

    alias['employees'] = ave.getTickerEmployeesNumber
    alias['address'] = ave.getTickerStreetAddress


    if datum in alias.keys():
        return str( (alias[datum])( str(ticker) ) )
    else:
        if datum == '_list_':
            return str( alias.keys() )
        if datum == '_list_col_':
            s = ""
            for k in alias.keys():
                s += k+ '\n'
            return s
        if datum == '_json_':
            _XX_ = OrderedDict()
            _XX_['is_keys'] = alias.keys()

            return json.dumps( _XX_ )
        return "#N/A %s" %(datum)

    return f
    return "Not Implemented"
    # Can return things like sector, industry, name, description, website url, employees, address
    # and other info which has no time associated with it.


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
            _XX_ = OrderedDict()
            _XX_['is_keys'] = alias.keys()
            _XX_['is_full'] = alias

            return json.dumps( _XX_ )
        return "#N/A %s" %(datum)


@app.route( '/api/info/<ticker>/bs/<datum>/<int:year>' ) #balance sheet
def lookup_ticker_balance_sheet( ticker, datum, year ):
    alias_assets = {}
    #current assets
    alias_assets['total_current_assets'] = 'Total Current Assets:None:None'
    alias_assets['total_accounts_receivable'] = 'Total Accounts Receivable:None:None'
    alias_assets['inventories'] = 'Inventories:None:None'
    alias_assets['ppe'] = 'Net Property, Plant & Equipment:None:None'
    alias_assets['other_current_assets'] = 'Other Current Assets:None:None'
    alias_assets['cash'] = 'Cash & Short Term Investments:Cash Only:None'
    alias_assets['short_term_investments'] = 'Cash & Short Term Investments:Short-Term Investments:None'

    #non-current assets
    alias_assets['total_investment_advances'] = 'Total Investments and Advances:None:None'
    alias_assets['long_term_receivable'] = 'Long-Term Note Receivable:None:None'
    alias_assets['intangible_assets'] = 'Intangible Assets:None:None'
    alias_assets['other_assets'] = 'Other Assets:None:None'

    alias_assets['total_assets'] = 'Total Assets:None:None'



    alias_liabilities = {}
    alias_liabilities['debt_payment_short_term'] = 'ST Debt & Current Portion LT Debt:Short Term Debt:None'
    alias_liabilities['debt_payment_long_term'] = 'ST Debt & Current Portion LT Debt:Current Portion of Long Term Debt:None'
    alias_liabilities['accounts_payable'] = 'Accounts Payable:None:None'
    alias_liabilities['income_tax_payable'] = 'Income Tax Payable:None:None'
    alias_liabilities['other_current_liabilities'] = 'Other Current Liabilities:None:None'
    alias_liabilities['total_current_liabilities'] = 'Total Current Liabilities:None:None'

    alias_liabilities['other_liabilities'] = 'Other Liabilities:None:None'
    alias_liabilities['total_liabilities'] = 'Total Liabilities:None:None'

    #ratio - TODO: consider removing this. calculate these ratios by yourself later
    alias_liabilities['current_ratio'] = 'Cash & Short Term Investments FOR CALCULATION PURPOSES ONLY:Current Ratio:None'
    alias_liabilities['quick_ratio'] = 'Cash & Short Term Investments FOR CALCULATION PURPOSES ONLY:Quick Ratio:None'
    alias_liabilities['cash_ratio'] = 'Cash & Short Term Investments FOR CALCULATION PURPOSES ONLY:Cash Ratio:None'



    if datum in alias_assets.keys():
        spl = alias_assets[datum].split(':')
        return str(ave.getTickerBalanceSheetAssetsDetails( ticker, year, spl[0], spl[1], spl[2] ))

    if datum in alias_liabilities.keys():
        spl = alias_liabilities[datum].split(':')
        return str(ave.getTickerBalanceSheetLiabilitiesDetails( ticker, year,  spl[0], spl[1], spl[2]  ))
    else:
        if datum == '_list_':
            return str( alias_assets.keys() )
        if datum == '_list_col_':
            s = "\n#Assets\n"
            for k in alias_assets.keys():
                s += k+ '\n'
            s += "\n#Liabilities\n"
            for k in alias_liabilities.keys():
                s += k+ '\n'
            return s
        if datum == '_json_':
            _XX_ = OrderedDict()
            _XX_['Assets'] = alias_assets.keys()
            _XX_['Liabilities'] = alias_liabilities.keys()
            _XX_['Assets_full'] = alias_assets
            _XX_['Liabilities_full'] = alias_liabilities
            return json.dumps( _XX_ )
        return "#N/A %s" %(datum)

    # return str(ave.getTickerBalanceSheetAssetsDetails( ticker, year, "Net Property, Plant & Equipment", "Accumulated Depreciation", "Construction in Progress" ))
    # return str(ave.getTickerBalanceSheetLiabilitiesDetails( ticker, year, 'None', "Quick Ratio" ))


@app.route( '/api/info/<ticker>/cf/<datum>/<int:year>' ) #cash flow statement
def lookup_ticker_cashflow_statement( ticker, datum, year ):
    alias_operating = {}
    alias_operating['net_operating_cashflow'] = "Net Operating Cash Flow:None:None"

    alias_investing = {}
    alias_investing['net_investing_cashflow'] = "Net Investing Cash Flow:None:None"
    alias_investing['capital_expense'] = "Capital Expenditures:None:None"
    alias_investing['acquisitions'] = "Net Assets from Acquisitions:None:None"
    alias_investing['sale_of_assets'] = "Sale of Fixed Assets & Businesses:None:None"
    alias_investing['from_financial_instruments'] = "Purchase/Sale of Investments:None:None"


    alias_financing = {}
    alias_financing['net_financing_cashflow'] = "Net Financing Cash Flow:None:None"
    alias_financing['free_cashflow'] = "Free Cash Flow:None:None"
    alias_financing['net_change_in_cash'] = "Net Change in Cash:None:None"
    alias_financing['dividend_paid'] = "Cash Dividends Paid - Total"
    alias_financing['debt_reduction'] = "Issuance/Reduction of Debt, Net:None:None"




    if datum in alias_operating.keys():
        spl = alias_operating[datum].split(':')
        return str( ave.getCashFlowOperatingActivityDetails(ticker, year, spl[0], spl[1], spl[2]))


    if datum in alias_investing.keys():
        spl = alias_investing[datum].split(':')
        return str( ave.getCashFlowInvestingActivityDetails(ticker, year, spl[0], spl[1], spl[2]))


    if datum in alias_financing:
        spl = alias_financing[datum].split(':')
        return str( ave.getCashFlowFinancingActivityDetails(ticker, year, spl[0], spl[1], spl[2]))


    if datum == '_json_':
        _XX_ = OrderedDict()
        _XX_['Operating Activity'] = alias_operating.keys()
        _XX_['Investing Activity'] = alias_investing.keys()
        _XX_['Financing Activity'] = alias_financing.keys()
        _XX_['Operating Activity_full'] = alias_operating
        _XX_['Investing Activity_full'] = alias_investing
        _XX_['Financing Activity_full'] = alias_financing

        return json.dumps( _XX_ )
    return "#N/A %s" %(datum)



    # return str( ave.getCashFlowOperatingActivityDetails(ticker, year, 'Other Funds'))
    # return str( ave.getCashFlowInvestingActivityDetails(ticker, year, 'Capital Expenditures'))
    # return str( ave.getCashFlowFinancingActivityDetails(ticker, year, 'Free Cash Flow'))



### Quote Calls
@app.route( '/api/info/<ticker>/quote/<field>/')
@app.route( '/api/info/<ticker>/quote/<field>/<date>')
def lookup_ticker_quote( ticker, field, date=None ):
    if field not in ['close', 'close_adj', 'volume', 'datetime', 'inserted_on', 'open', 'high', 'low']:
        return "invalid quote field"
    return ave.getTickerDailyQuote(ticker, date=date, field=field)



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

@app.route( '/api/list/<industry>/<sector>/company_list/')
@app.route( '/api/list/<industry>/<sector>/company_list/<xchange>')
def lookup_company_list( industry, sector, xchange=None ):
    industry = industry.replace( '_', '/' )
    sector = sector.replace( '_', '/' )

    if industry == 'None':
        industry = None
    if sector == 'None':
        sector = None

    #TODO Current xchange can only be 1 exchange. Implement xchange to be a comma separated list
    list_of_companies = ave.getCompanyName_FilterByIndustrynSector( industry=industry, sector=sector, bourse=xchange )
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

@app.route( '/industryInfo/collapsibleList/')
@app.route( '/industryInfo/collapsibleList/<xchange>')
def show_collapsible_list(xchange=None):
    INFO = {}
    for industry in sorted( ave.getIndustryList() ):
        INFO[industry] = {}
        for sector in sorted(ave.getSectorsOf( industry )):
            INFO[industry][sector] = ave.getCompanyName_FilterByIndustrynSector( industry, sector, bourse=xchange )

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
