# Sun Dance - Security Analysis
---


## Motivation and Description
A fun project to identify under valued assets, mainly securities analysis. 

I basically built a web-crawler to retrive financial statements (income statements, 
balance sheet, cashflow statements).

Read books especially from value investors like Ben Graham etc. I will put a list
of interesting books and ideas later. 

Currently available exchanges : HK, NSE(India), BSE(India), NYSE, NASDAQ, AMEX, TYO (Tokyo), SZSE (Shenzen), SSE (Shanghai)

Transfer some of the machine learning techniques to analyse and potentially make a
buck or two. 

## Daemon Usage 
It is possible to write config files to specify multiple processes and repeat structure. Most common config files is to retrive all the WSJ data and the 100-day quotes data. It is usually a good idea
to log everything to an external server. 

**Logging Server**
```
socat TCP4-LISTEN:9595,fork STDOUT
```

**WSJ Data**
```
python sundance_multi.py  -f config/retrive-parse-insert.config.xml --logserver localhost:9595
```

**100d Quotes Data**
```
python sundance_multi.py  -f config/retrive-parse-insert-recent-quotes.config.xml --logserver localhost:9595
```


## Core Usage 
```
python data_retriver.py  -sd equities_db/data__N -ld equities_db/lists --wsj --xhkex --xbse --xnse

python data_parser.py --wsj -sd equities_db/data__N -ld equities_db/lists/  --xhkex --xbse --xnse

python data_inserter.py --wsj -db equities_db/data__N -l equities_db/lists/ --xhkex --xbse --xnse
```

#### Delete Raw (WSJ)
```
python data_parser.py --delete_raw_wsj -sd equities_db/data__N -ld equities_db/lists/  --xhkex --xbse --xnse
```

#### Daily Quote Data (currently only for HKEX, NSE)
```
python  data_retriver.py -sd equities_db/data__quotes_N -ld equities_db/lists --quotes_full --xnse --xhkex

python  data_retriver.py -sd equities_db/data__quotes_N -ld equities_db/lists --quotes_recent --xnse --xhkex

python  daily_quote_inserter.py -db equities_db/data__quotes_N -ld equities_db/lists --xnse --xhkex 
```

#### Verbose
```
python data_retriver.py -v 1  -sd equities_db/data__N -ld equities_db/lists --wsj --xhkex --xbse --xnse

python data_parser.py --hkex --wsj -sd equities_db/data__N -ld equities_db/lists/ -v 1 --delete_raw --xhkex --xbse --xnse
```

#### First time usage 
Populate list of stocks from various exchanges. You might also want to look at `test_pkg.py` which is a cummulation of all the required pakages.

```
python init_lister.py
```

## MongoDB Schema
I insert individual elements into flat mongodb structure. Note that the code might not be exactlty as described in document, but is more or less consistent. 

Details of Schema : [HERE](documents/mongodb_schema_details.md)


## Study Resources
List of books, articles, other resources to learn on investing [HERE](documents/economics_theory/)

## Software Licence
![License ICO](documents/images/88x31.png)
This software is being released under the [Creative Commons Attribution-NonCommerial License](https://creativecommons.org/licenses/by-nc/4.0/legalcode). 


Licensees may copy, distribute, display and perform the work and make derivative works and remixes based on it only if they give the author or licensor the credits (attribution) in the manner specified by these.
Licensees may copy, distribute, display, and perform the work and make derivative works and remixes based on it only for non-commercial purposes.
For commerial license please contact the author. 

## Author
Manohar Kuse <mpkuse@connect.ust.hk>

If you like this you might be interested in its [sister projects](http://github.com/RInvestments). 

