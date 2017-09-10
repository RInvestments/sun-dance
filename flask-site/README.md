# Flask site for sun dance.

Currently we use flask to provide easy to use API of the database info, for other web applications.
The entire flask site is organized under `/flask-site`.
It queries data from the mongodb database.


## How to run
```
export FLASK_APP=site-entry.py
export FLASK_DEBUG=1

python -m flask run

```

## Webservice Info
`site-entry.py` provides for main of the web based interface. Currently,
we provide some simple web based tools to get info from the database. We
also provide a API under `/api/` of the flask site. For a more detailed
and upto date info have a look at `site-entry.py` which defines an URL
and its associated callback functions.

Note that these call back functions
are not supposed to query the database directly, but it is to be done
using the `MongoQuery` class provided in file `MongoQuery.py`. This
class provides various functions to query the mongodb database. In the future
can create more classes to give access to various parts of database.

The api is organized into 2 parts.

- Returns a data item about a ticker
    * Only ticker name is required, eg. company name etc, [here](#info), [here](#info-details)
    * Data on income statement. Needs ticker name, field name, year/quater [here](#info-on-income-statement)
    * Data on balance sheet. Needs ticker name, field name, year/quater [here](#info-on-balance-sheet)
    * Data on cashflow statement sheet. Needs ticker name, field name, year/quater [here](#info-on-cashflow-statement)
    * Daily quote [here](#quote-data)

- Returns a list
    * Of companies given a (industry, sector) pair.
    * Of industries
    * Of sectors given an industry



## Data on Ticker
This section is about info (timed and untimed) about a ticker.
Use the URLs below to get the needed info.

### Info
URL : ``/api/info/<ticker>``<br/>


### Info Details
URL : ``/api/info/<ticker>/<datum>``<br/>

datum :
```json
"is_keys": [
  "sector",
  "industry",
  "description",
  "name",
  "desc"
  "employees"
  "address"
]
```


### Info on Income Statement
URL : ``/api/info/<ticker>/is/<datum>/<int:year>``<br/>

year : Eg. 2016, 20160630 etc.  

datum :
```json
is_keys: [
    "income_gross",
    "revenue",
    "cogs",
    "expense_tax",
    "income_pretax",
    "expense_interest",
    "eps_diluted",
    "income_net",
    "eps_basic",
    "expense_sga",
    "ebit",
    "eps",
    "ebitda",
    "shares_outstanding"
]
```

### Info on Balance Sheet
URL : ``/api/info/<ticker>/bs/<datum>/<int:year>``<br/>

datum :
```json
Assets: [
    "total_investment_advances",
    "total_current_assets",
    "short_term_investments",
    "ppe",
    "long_term_receivable",
    "cash",
    "other_assets",
    "total_accounts_receivable",
    "total_assets",
    "intangible_assets",
    "inventories",
    "other_current_assets"
],

Liabilities: [
    "debt_payment_long_term",
    "total_current_liabilities",
    "other_liabilities",
    "accounts_payable",
    "quick_ratio",
    "cash_ratio",
    "other_current_liabilities",
    "current_ratio",
    "total_liabilities",
    "income_tax_payable",
    "debt_payment_short_term"
]
```

### Info on Cashflow Statement
URL : ``/api/info/<ticker>/cf/<datum>/<int:year>``<br/>

datum :
```json
Operating Activity: [
    "net_operating_cashflow"
],
Investing Activity: [
    "acquisitions",
    "capital_expense",
    "net_investing_cashflow",
    "from_financial_instruments",
    "sale_of_assets"
],
Financing Activity: [
    "debt_reduction",
    "dividend_paid",
    "net_financing_cashflow",
    "net_change_in_cash",
    "free_cashflow"
]
```

### Quote Data
URL : ``/api/info/<ticker>/quote/<field>/<date>``
date : 2016-07-15. Not giving date will return latest quote.

field :
```json
['close', 'close_adj', 'volume', 'datetime', 'inserted_on', 'open', 'high', 'low']
```



## Returns a list
These set of urls provides various lists

### Companies List
URL : `/api/list/<industry>/<sector>/company_list/<xchange>`

This is the most useful function. xchange set to None will give companies from all exchanges. Can also specify xchange like HK. Currently comma
separated list is not supported. Will implement this later.

### Industry List
URL : ``/api/list/industry_list``

Returns a comma separated list of industries.

### Sector List
URL : ``/api/list/<industry>/sector_list'``

Returns a comma separated list of sectors of
specified industry.




## Author
Manohar Kuse <mpkuse@connect.ust.hk>
