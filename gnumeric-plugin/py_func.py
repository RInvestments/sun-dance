from Gnumeric import *
import Gnumeric as g
import string
import urllib2
import datetime
# http://www.bruunisejs.dk/PythonHacks/rstFiles/500%20Notes%20on%20spreadsheets%20etc.html

# # Here is a function with variable number of arguments
# def func_printf(format, *args):
# 	'@FUNCTION=PY_PRINTF\n'\
# 	'@SYNTAX=PY_PRINTF (format,...)\n'\
# 	'@DESCRIPTION='\
# 	'\n'\
# 	'@EXAMPLES=\n'\
# 	'PY_PRINTF("Test: %.2f",12) equals "Test: 12.00")'\
# 	'\n'\
# 	'@SEEALSO='
#
# 	try:
# 		val = format % args
# 	except TypeError:
# 		raise GnumericError, GnumericErrorVALUE
# 	else:
# 		return val
#
# # Here is a function with one argument
# def func_capwords(str):
# 	'@FUNCTION=PY_CAPWORDS\n'\
# 	'@SYNTAX=PY_CAPWORDS (sentence)\n'\
# 	'@DESCRIPTION='\
# 	'\n'\
# 	'@EXAMPLES=\n'\
# 	'PY_CAPWORDS("Hello world") equals "Hello World")'\
# 	'\n'\
# 	'@SEEALSO='
#
# 	return string.capwords(str)
#
# # Here is a function which calls a spreadsheet function
# def func_bitand(num1, num2):
# 	'@GNM_FUNC_HELP_NAME@BITAND:bitwise AND of its two arguments.\n'\
# 	'@GNM_FUNC_HELP_ARG@number1:first value\n'\
# 	'@GNM_FUNC_HELP_ARG@number2:second value\n'\
# 	'@GNM_FUNC_HELP_EXAMPLES@=PY_BITAND(12, 6)\n'\
# 	'@GNM_FUNC_HELP_SEEALSO@BITAND'
# 	gnm_bitand=functions['bitand']
# 	return gnm_bitand(num1, num2)
SERVER = 'http://127.0.0.1:5000'

def square_me( a ):
	return a**2


def api_call( ticker, field ):
	url_db = {}
	url_db['name'] = '/api/info/%s' %(ticker)
	url_db['industry'] = '/api/info/%s/industry' %(ticker)
	url_db['sector'] = '/api/info/%s/sector' %(ticker)
	url_db['employees'] = '/api/info/%s/employees' %(ticker)
	url_db['description'] = '/api/info/%s/description' %(ticker)
	url_db['address'] = '/api/info/%s/address' %(ticker)
	



	url_db['quote_lastclose'] = '/api/info/%s/quote/close' %(ticker)
	url_db['lastclose'] = url_db['quote_lastclose']
	url_db['quote_lastvolume'] = '/api/info/%s/quote/volume' %(ticker)
	url_db['lastvolume'] = url_db['quote_lastvolume']
	url_db['quote_lastdatetime'] = '/api/info/%s/quote/datetime' %(ticker)
	url_db['lastdatetime'] = url_db['quote_lastdatetime']

	if str(field) in url_db.keys():
		URL = SERVER+url_db[field]
		strr = urllib2.urlopen(URL).read()
		try:
			return float(strr)
		except:
			return strr
	else:
		return "api_call/NA"


	return "api_call INVALID FIELD"

# input days since 1899-12-31 (date = 0). Which is a standard date format for spreadsheets
def days_to_date( days_since_ ):
	delta = datetime.timedelta( days=(int(days_since_)-2) )
	base = datetime.datetime.strptime("1900-01-01","%Y-%m-%d")
	return datetime.datetime.strftime( base+delta, '%Y-%m-%d' )

def api_call_quote_timed( ticker,field,year ):
	url_db = {}
	# From Daily Quote Data
	url_db['close' ] = '/api/info/%s/quote/close/%s' %(ticker,days_to_date( year ))
	url_db['close_adj' ] = '/api/info/%s/quote/close_adj/%s' %(ticker,days_to_date( year ))
	url_db['volume' ] = '/api/info/%s/quote/volume/%s' %(ticker,days_to_date( year ))
	url_db['datetime' ] = '/api/info/%s/quote/datetime/%s' %(ticker,days_to_date( year ))
	url_db['inserted_on' ] = '/api/info/%s/quote/inserted_on/%s' %(ticker,days_to_date( year ))
	url_db['open' ] = '/api/info/%s/quote/open/%s' %(ticker,days_to_date( year ))
	url_db['high' ] = '/api/info/%s/quote/high/%s' %(ticker,days_to_date( year ))
	url_db['low' ] = '/api/info/%s/quote/low/%s' %(ticker,days_to_date( year ))

	if str(field) in url_db.keys():
		# return datetime.datetime.strftime( (datetime.datetime.strptime("1900-01-01","%Y-%m-%d") + datetime.timedelta( days=int(year)-1 ) ) ), '%Y-%m-%d' )
		# return str(days_to_date( year ))
		URL = SERVER+url_db[field]
		# return URL
		strr = urllib2.urlopen(URL).read()
		try:
			return float(strr)
		except:
			return strr
	else:
		return "api_call_quote_timed NA/ %s" %(str(field))

	# if field == "revenue":
	# 	URL = SERVER+'/api/info/%s/revenue/%d' %(ticker,year)
	# 	# return URL
	# 	return urllib2.urlopen(URL).read()

	return "#NA %s" %(field)



def api_call_timed( ticker,field,year ):
	# return "Hello %s %s %s" %(str(ticker), str(field), str(year))
	url_db = {}
	# From Income Statement
	url_db['revenue'] = '/api/info/%s/is/revenue/%d' %(ticker,year)
	url_db['cogs' ] = '/api/info/%s/is/cogs/%d' %(ticker,year)
	url_db['income_gross' ] = '/api/info/%s/is/income_gross/%d' %(ticker,year)
	url_db['income_pretax' ] = '/api/info/%s/is/income_pretax/%d' %(ticker,year)
	url_db['income_net' ] = '/api/info/%s/is/income_net/%d' %(ticker,year)
	url_db['expense_sga' ] = '/api/info/%s/is/expense_sga/%d' %(ticker,year)
	url_db['expense_interest' ] = '/api/info/%s/is/expense_interest/%d' %(ticker,year)
	url_db['expense_tax' ] = '/api/info/%s/is/expense_tax/%d' %(ticker,year)
	url_db['ebit' ] = '/api/info/%s/is/ebit/%d' %(ticker,year)
	url_db['ebitda' ] = '/api/info/%s/is/ebitda/%d' %(ticker,year)
	url_db['eps' ] = '/api/info/%s/is/eps/%d' %(ticker,year)
	url_db['eps_basic' ] = '/api/info/%s/is/eps_basic/%d' %(ticker,year)
	url_db['eps_diluted' ] = '/api/info/%s/is/eps_diluted/%d' %(ticker,year)
	url_db['shares_outstanding' ] = '/api/info/%s/is/shares_outstanding/%d' %(ticker,year)


	# From Balance SHeet/Assets
	url_db['total_assets'] = '/api/info/%s/bs/total_assets/%d' %(ticker,year)
	url_db['total_current_assets'] = '/api/info/%s/bs/total_current_assets/%d' %(ticker,year)
	url_db['total_accounts_receivable'] = '/api/info/%s/bs/total_accounts_receivable/%d' %(ticker,year)
	url_db['inventories'] = '/api/info/%s/bs/inventories/%d' %(ticker,year)
	url_db['ppe'] = '/api/info/%s/bs/ppe/%d' %(ticker,year)
	url_db['other_current_assets'] = '/api/info/%s/bs/other_current_assets/%d' %(ticker,year)
	url_db['cash'] = '/api/info/%s/bs/cash/%d' %(ticker,year)
	url_db['short_term_investments'] = '/api/info/%s/bs/short_term_investments/%d' %(ticker,year)

	url_db['total_investment_advances'] = '/api/info/%s/bs/total_investment_advances/%d' %(ticker,year)
	url_db['long_term_receivable'] = '/api/info/%s/bs/long_term_receivable/%d' %(ticker,year)
	url_db['intangible_assets'] = '/api/info/%s/bs/intangible_assets/%d' %(ticker,year)
	url_db['other_assets'] = '/api/info/%s/bs/other_assets/%d' %(ticker,year)

	# From Balance sheet/Liabilities
	url_db['debt_payment_short_term'] = '/api/info/%s/bs/debt_payment_short_term/%d' %(ticker,year)
	url_db['debt_payment_long_term'] = '/api/info/%s/bs/debt_payment_long_term/%d' %(ticker,year)
	url_db['accounts_payable'] = '/api/info/%s/bs/accounts_payable/%d' %(ticker,year)
	url_db['income_tax_payable'] = '/api/info/%s/bs/income_tax_payable/%d' %(ticker,year)
	url_db['other_current_liabilities'] = '/api/info/%s/bs/other_current_liabilities/%d' %(ticker,year)
	url_db['total_current_liabilities'] = '/api/info/%s/bs/total_current_liabilities/%d' %(ticker,year)
	url_db['other_liabilities'] = '/api/info/%s/bs/other_liabilities/%d' %(ticker,year)
	url_db['total_liabilities'] = '/api/info/%s/bs/total_liabilities/%d' %(ticker,year)

	# From cash_flow_statement
	url_db['net_operating_cashflow'] = '/api/info/%s/cf/net_operating_cashflow/%d' %(ticker,year)

	url_db['net_investing_cashflow'] = '/api/info/%s/cf/net_investing_cashflow/%d' %(ticker,year)
	url_db['capital_expense'] = '/api/info/%s/cf/capital_expense/%d' %(ticker,year)
	url_db['acquisitions'] = '/api/info/%s/cf/acquisitions/%d' %(ticker,year)
	url_db['sale_of_assets'] = '/api/info/%s/cf/sale_of_assets/%d' %(ticker,year)
	url_db['from_financial_instruments'] = '/api/info/%s/cf/from_financial_instruments/%d' %(ticker,year)

	url_db['net_financing_cashflow'] = '/api/info/%s/cf/net_financing_cashflow/%d' %(ticker,year)
	url_db['free_cashflow'] = '/api/info/%s/cf/free_cashflow/%d' %(ticker,year)
	url_db['net_change_in_cash'] = '/api/info/%s/cf/net_change_in_cash/%d' %(ticker,year)
	url_db['dividend_paid'] = '/api/info/%s/cf/dividend_paid/%d' %(ticker,year)
	url_db['debt_reduction'] = '/api/info/%s/cf/debt_reduction/%d' %(ticker,year)

	if str(field) in url_db.keys():
		# return datetime.datetime.strftime( (datetime.datetime.strptime("1900-01-01","%Y-%m-%d") + datetime.timedelta( days=int(year)-1 ) ) ), '%Y-%m-%d' )
		# return str(days_to_date( year ))
		URL = SERVER+url_db[field]
		# return URL
		strr = urllib2.urlopen(URL).read()
		try:
			return float(strr)
		except:
			return strr
	else:
		return "api_call_timed NA/ %s" %(str(field))

	# if field == "revenue":
	# 	URL = SERVER+'/api/info/%s/revenue/%d' %(ticker,year)
	# 	# return URL
	# 	return urllib2.urlopen(URL).read()

	return "#NA %s" %(field)


def api_list_industry( cell ):
	wbs = g.workbooks()
	wb = wbs[0]
	sheet = wb.sheets()[0]


	col = g.functions['column']
	row = g.functions['row']

	URL = SERVER+'/api/list/industry_list'
	info = urllib2.urlopen(URL).read()



	for i, data in enumerate(info.split(',')):
		sheet.cell_fetch( int(col(cell))-1, i+int(row(cell))-1 ).set_text( data )

	# return str( col(cell) )+','+ str( row(cell))


# Giveout sectors given an industry
def api_list_sector( industry, cell ):
	wbs = g.workbooks()
	wb = wbs[0]
	sheet = wb.sheets()[0]


	col = g.functions['column']
	row = g.functions['row']

	URL = SERVER+urllib2.quote('/api/list/%s/sector_list' %(industry.replace("/","_")))
	# return URL
	info = urllib2.urlopen(URL).read()


	for i, data in enumerate(info.split(',')):
		sheet.cell_fetch( int(col(cell))-1, i+int(row(cell))-1 ).set_text( data )

	return industry

# Given an Industry and a sector, split of all the companies tickers
def api_list_companies( industry, sector, bourse, cell ):
	wbs = g.workbooks()
	wb = wbs[0]
	sheet = wb.sheets()[0]


	col = g.functions['column']
	row = g.functions['row']

	URL = SERVER+urllib2.quote('/api/list/%s/%s/company_list/%s' %(industry.replace("/","_"),sector.replace("/","_"),bourse ))

	# return URL
	info = urllib2.urlopen(URL).read()


	for i, data in enumerate(info.split(',')):
		sheet.cell_fetch( int(col(cell))-1, i+int(row(cell))-1 ).set_text( data )

	return industry+','+sector+str(len(info.split(',')))

test_functions = {
	# Here we tell Gnumeric that the Python function 'func_printf'
	# provides the spreadsheet function 'py_printf', and that
	# 'py_printf' may be called with any number of arguments [1].
	# 'py_printf': func_printf,
	'square_me': ('f', 'a', square_me),
	'SUNDANCE_INFO' : ('ss', 'ticker,field', api_call),
	'SUNDANCE' : ('sss', 'ticker,field,year', api_call_timed),
	'SUNDANCE_QUOTE' : ('sss', 'ticker,field,year', api_call_quote_timed),
	'SUNDANCE_INDUSTRY_LIST' : ( 'r', 'cell', api_list_industry ),
	'SUNDANCE_SECTOR_LIST' : ( 'sr', 'industry,cell', api_list_sector ),
	'SUNDANCE_COMPANY_LIST' : ( 'sssr', 'industry,sector,bourse,cell', api_list_companies ),
	'SD_INFO' : ('ss', 'ticker,field', api_call),
	'SD' : ('sss', 'ticker,field,year', api_call_timed),
	'SD_QUOTE' : ('sss', 'ticker,field,year', api_call_quote_timed),
	'SD_INDUSTRY_LIST' : ( 'r', 'cell', api_list_industry ),
	'SD_SECTOR_LIST' : ( 'sr', 'industry,cell', api_list_sector ),
	'SD_COMPANY_LIST' : ( 'sssr', 'industry,sector,bourse,cell', api_list_companies )

	# 'func_capwords' provides the spreadsheet function 'py_capwords'.
	# 'py_capwords' should be called with a single argument.
	# This should be a string ('s'), and the argument name is 'sentence'.
	# 'py_capwords': ('s', 'sentence', func_capwords),

	# 'func_bitand' provides 'bitand', which should be called with two
	# numeric arguments (ff) named 'num1' and 'num2'.
	# 'py_bitand':   ('ff', 'num1, num2', func_bitand)
}


# [1] Actually, the 'def func_printf' statement says that it requires at least
#     one argument. But there is no way to express that in the syntax used in
#     the 'test_functions' dictionary.
