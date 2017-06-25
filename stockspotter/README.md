#stockspotter

This package is the core of this project. Here is a brief summary of sub-packages.

### db
This sub-packages provide for classes to handle data sources. Each class
is equiped to handle 1 data source. A typical class provides mechanism to retrive raw data. Process/Parse this raw data into a json file. Finally it also gives mechanism to load the parsed data. 

I am planning to use WSJ as primary data source for financial statements. For now it is tailored for HKEX. 

### lister
This sub-package provides classes to a) to retrive list of all securities listed (currently, HKEX, BSE, NSE, more can easily be added with some effort). Further, it provides classes like HSILister etc to make a list of various of the bench mark indices. for example Hang Seng index etc. Plans to add retrival from more sources in the future (official sources only). 

Basically, to add more exchanges, need to find an official list of stocks on this exchange. Currently
have done so for HKEX, BSE, NSE. Although adding more exchanges is not a priority (as I cannot currently have teeth to buy stocks there), I plan to do it as I find time. I would like to have exchanges of Shanghai, Shenzen, NYSE, NASDAQ, DAX, Korean Exchange, Taipei, Japan, Singapore, London. 


### touchstone
* deprecated. Soon I plan to remove this, as now my thinking is to add all the data to a mongodb engine. All further calculations, analysis etc shall be done using a separate web-based engine package like FLASK or similar. 

Provides classes to measure various ratios, models, metric for individual stocks from their financial statements. To start with will implement [5-must have ratios](http://www.investopedia.com/articles/fundamental-analysis/09/five-must-have-metrics-value-investors.asp). After than to have more of the fundamental ratios like for example [investopedia](http://www.investopedia.com/university/ratio-analysis/using-ratios.asp), [wikipedia](https://en.wikipedia.org/wiki/Financial_ratio)

On a more academic front [a](http://educ.jmu.edu/~drakepp/general/index.html) and [b](http://educ.jmu.edu/~drakepp/principles/module2/fin_rat.pdf)

After having computational teeth for basic ratios at hand, would go for model based approaches like [DCF](https://en.wikipedia.org/wiki/Discounted_cash_flow) etc. 


## Notes
- This package be as simple and user friendly and small as possible. It basically just provides way to parse a html page for data