# Sun Dance - Security Analysis
---


## Motivation and Description
A fun project to identify under valued assets, mainly securities analysis. 

I basically built a web-crawler to retrive financial statements (income statements, 
balance sheet, cashflow statements).

Read books especially from value investors like Ben Graham etc. Other
sources like investopedia etc to build scripts that can scan all the listings of 
HKEX. It is easy to add more source (need work).
Currently can do HKEX, BSE(India), NSE(India)

Transfer some of the machine learning techniques to analyse and potentially make a
buck or two. 

## Core Usage 
python -i data_retriver.py  -sd equities_db/data__N -ld equities_db/lists --wsj --xhkex --xbse --xnse

python data_parser.py --wsj -sd equities_db/data__N -ld equities_db/lists/  --xhkex --xbse --xnse

python data_inserter.py (currently no commandline parsing. adjust db_prefix param)

#### Delete Raw (WSJ)
python data_parser.py --delete_raw_wsj -sd equities_db/data__N -ld equities_db/lists/  --xhkex --xbse --xnse

#### Daily Quote Data (currently only for HKEX, NSE)
python -i data_retriver.py -sd equities_db/data__quotes -ld equities_db/lists --yahoo_historical --xnse --xhkex

python -i  daily_quote_inserter.py (currently no commandline parsing. adjust db_prefix and should work)
#### Verbose
python -i data_retriver.py -v 1  -sd equities_db/data__N -ld equities_db/lists --wsj --xhkex --xbse --xnse

python data_parser.py --hkex --wsj -sd equities_db/data__N -ld equities_db/lists/ -v 1 --delete_raw --xhkex --xbse --xnse

#### First time usage 
Populate list of stocks from various exchanges
python test_lister.py 

## MongoDB Schema
I insert individual elements into flat mongodb structure. Note that the code might not be exactlty as described in document, but is more or less consistent. 

Details of Schema : [HERE](documents/mongodb_schema_details.md)


## Study Resources
List of books, articles, other resources to learn on investing [HERE](documents/economics_theory/README.md)

## Software Licence
![License ICO](documents/images/88x31.png)
This software is being released under the [Creative Commons Attribution-NonCommerial License](https://creativecommons.org/licenses/by-nc/4.0/legalcode). 


Licensees may copy, distribute, display and perform the work and make derivative works and remixes based on it only if they give the author or licensor the credits (attribution) in the manner specified by these.
Licensees may copy, distribute, display, and perform the work and make derivative works and remixes based on it only for non-commercial purposes.
For commerial license please contact the author. 

## Author
Manohar Kuse <mpkuse@connect.ust.hk>

