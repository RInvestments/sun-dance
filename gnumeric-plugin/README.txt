# GNUMERIC Plugin.

This plugin provides for user defined functions in gnumeric (a spreadsheet program from GNU).
Python can be used to define these functions. Essentially this provides hook to call
python functions from gnumeric spreadsheet. My python functions than connect to
the flask-site (stock api) via http to retrive requested stock data.

## Files
- plugin.xml : List of user defined functions
- py_func.py : This file defines each of the custom-functions in python.


## Gnumeric Functions Doc
Calls can be categorized as a) returning a list; b) ticker info untimed; c) ticker info timed

### Returning a list
- SD_INDUSTRY_LIST( cell ) : List of industries. put data into `cell`
- SD_SECTOR_LIST( industry_str, cell) : Given an industry get its sectors
- SD_COMPANY_LIST( industry, sector, bourse, cell ) : List of companies in this industry, sector for a specified bourse


### Ticker Info
- SD_INFO( ticker, *datum* )
  * name
  * industry
  * sector
  * employees
  * description
  * quote_lastclose
  * lastclose
  * quote_lastvolume
  * lastvolume
  * quote_lastdatetime
  * lastdatetime

### Ticker Info (Timed)
- SD( ticker, *field*, *year*)
      - **Income Statement**
      * 'revenue'
      * 'cogs'
      * 'income_gross'
      * 'income_pretax'
      * 'income_net'
      * 'expense_sga'
      * 'expense_interest'
      * 'expense_tax'
      * 'ebit'
      * 'ebitda'
      * 'eps'
      * 'eps_basic'
      * 'eps_diluted'
      * 'shares_outstanding'


      - **Balance SHeet/Assets**
      * 'total_assets'
      * 'total_current_assets'
      * 'total_accounts_receivable'
      * 'inventories'
      * 'ppe'
      * 'other_current_assets'
      * 'cash'
      * 'short_term_investments'
      * 'total_investment_advances'
      * 'long_term_receivable'
      * 'intangible_assets'
      * 'other_assets'

      - **Balance sheet/Liabilities**
      * 'debt_payment_short_term'
      * 'debt_payment_long_term'
      * 'accounts_payable'
      * 'income_tax_payable'
      * 'other_current_liabilities'
      * 'total_current_liabilities'
      * 'other_liabilities'
      * 'total_liabilities'

      - **cash_flow_statement**
      * 'net_operating_cashflow'

      * 'net_investing_cashflow'
      * 'capital_expense'
      * 'acquisitions'
      * 'sale_of_assets'
      * 'from_financial_instruments'

      * 'net_financing_cashflow'
      * 'free_cashflow'
      * 'net_change_in_cash'
      * 'dividend_paid'
      * 'debt_reduction'



Need to put this folder (possibly its softlink also should be ok!) in:
/home/mpkuse/.gnumeric/1.12.28/plugins/kuse-py-func

## References
This plugin is made from templates and example provided in links below. Note that gnumeric is
an extremely buggy program. I am using it just because it is very straight forward to write
plugins for it.

https://help.gnome.org/users/gnumeric/stable/sect-extending-python.html.en

http://www.bruunisejs.dk/PythonHacks/rstFiles/500%20Notes%20on%20spreadsheets%20etc.html
