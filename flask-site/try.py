from pymongo import MongoClient
from MongoQueries import MongoQueries

# MongoDB
client = MongoClient()
db = client.universalData.universalData

ave = MongoQueries(client)
# print ave.getCompanyName( '2333.HK' )
# p=ave.getIndustryList()
# p = ave.getSectorsOf( industryName='Automotive' )
# p = ave.getCompanyName( industry='Technology', sector='Software')


# INFO = {}
# for industry in sorted( ave.getIndustryList() ):
#     INFO[industry] = {}
#     for sector in sorted(ave.getSectorsOf( industry )):
#         INFO[industry][sector] = ave.getCompanyName_FilterByIndustrynSector( industry, sector )

print ave.getTickerDailyQuote( "2208.HK", '2017-07-05', 'close' )

print ave.getTickerBalanceSheetAssetsDetails( "2333.HK", 2016, "Total Assets")
print ave.getTickerEmployeesNumber( '2333.HK')
quit()

# ary = ave.getCompanyRevenue(bourse='BSE')
print 'Revenue', ave.getTickerIncomeStatementDetails( '2333.HK', 2016, 'Sales/Revenue' )
print 'COGS', ave.getTickerIncomeStatementDetails( '2333.HK', 2016, 'Cost of Goods Sold (COGS) incl. D&A' )
print 'SG&A', ave.getTickerIncomeStatementDetails( '2333.HK', 2016, 'SG&A Expense' )
print 'Income Tax', ave.getTickerIncomeStatementDetails( '2333.HK', 2016, 'Income Tax' )
print 'Net Income Available to Common', ave.getTickerIncomeStatementDetails( '2333.HK', 2016, 'Net Income Available to Common' )
ticker = '2333.HK'
revenue = ave.getTickerIncomeStatementDetails( ticker, 2016, 'Sales/Revenue' )
cogs = ave.getTickerIncomeStatementDetails( ticker, 2016, 'Cost of Goods Sold (COGS) incl. D&A' )
sga = ave.getTickerIncomeStatementDetails( ticker, 2016, 'SG&A Expense' )
income_tax = ave.getTickerIncomeStatementDetails( ticker, 2016, 'Income Tax' )
net_income = ave.getTickerIncomeStatementDetails( ticker, 2016, 'Net Income Available to Common' )
interest_exp = revenue - cogs - sga - income_tax - net_income
print 'Interest Expense : ', interest_exp
