# MongoDB Schema Details

## Basics
All data is organized in a collection as an heirarchy. 

industry > sector > company > type1 > type2 .... > type7

Industry, sector, company are mandatory for each entry. However type1 ... type7 is free-flow and depends on the data. However, type1,type2, and type3 usually will be present. See details in later sections. The values are stored raw-string in `value_string` and interpreted in `val`

For a tree on (industry,sector) see [here](industry_list_wsj_anytree.txt)


## Statement Type - type1
This denotes the type of statement. It will be one of the values

- [Financials](#financials)
- [Profile](#profile)
- [Executives](#executives)
- [Ownership](#ownership)
- [Financial Statements](#financial-statements)

## Financials
[Example json](example_json/financials_pp.json). This uses `type2` and `type3` only.

Type2 are one of 

1. Ratios and Margins
2. Earnings and Estimates
3. Per Share Data

## Profile
[Example json](example_json/wsj_profile_pp.json).
This uses `type2` and `type3` only.

## Executives
[Example json](example_json/companyExecutives_pp.json). Uses type2 like `10#Pui Hung`. This means the ordering is 10 and the name of the executive is Pui Hung. Both separated with a `#`. The order is the order inwhich they appear, usually by authority. 

`type3` can be one of 

1. Current Position
2. Description 
3. Age
4. Since
5. Value
6. order 
7. Fiscal Year Total
8. Options

## Ownership
[Example json](example_json/institutional_investors_pp.json). Uses type2 to denote if the entry is a) Institutional Investor or b) Mutual Funds

type3 is the name of the mutual fund/institution. 
type4 has the fields viz. 

1. Percent Shares Out
2. Percent of Assets
3. Change In Shares
4. Shares Held
5. As of Date


## Financial Statements
The heirarchy is the most complex one. This also occupies about 90% of the datasize of this DB. 

#### type1:

'Financial Statements'



#### type2 and type3:
In general the sheets are as follows. Note that sheets in different industries might be slightly different than the examples here. Further not all industries/companies follow the [GAAP](https://en.wikipedia.org/wiki/Accounting_standard) accounting practice. Notably the sheets on Banking and Financial services industries are very different. Care need to be excerised here. 

1. income_statement
    * None [json](example_json/income_statement.a_pp.json)
2. balance_sheet 
    * assets [json](example_json/balance_sheet.a.assets_pp.json)
    * liabilities [json](example_json/balance_sheet.a.liabilities_pp.json)
3. cash_flow_statement
    * operating [json](example_json/cash_flow_statement.a.operating_pp.json)
    * investing [json](example_json/cash_flow_statement.a.investing_pp.json)
    * financing [json](example_json/cash_flow_statement.a.financing_pp.json)
    
#### type4 and period:
This also uses another field called period. Whose values will be either of 'a' or 'q'. 

'a' is to denote that this data is annual data for the year specified in `type4`. Example of `type4`: 2013, 2011 etc.


'q' is to denote quaterly data for the quater ending
on the date specified in type4. In type4 the dates are specified as integers. For example 30-Sep-2000 is denoted as 20000930. This is done thus so that numerical comparisons can be used if need be (for sorting).


#### type5, type6 and type7:
This is used for the heirarchy in each of the statements. For details of this refer to the example json in above sub-section. 
