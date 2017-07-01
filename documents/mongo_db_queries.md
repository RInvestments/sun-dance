### Find 
db.getCollection('universalData').find({'type1':'Ownership', 'type2':'Institutional Investor','type3': /Sachs/, 'type4': 'Change In Shares'})

## Sort by Revenues
db.universalData.find({  'industry':'Technology', 'type1':'Profile', 'type2':'Company Info', 'type3':'Sales or Revenue'} ).sort( {'val':-1} )


## Aggregate


## Aggregate and match
db.getCollection('universalData').aggregate(  {$match:{'industry':'Automotive'}}, {$group: {_id:'$sector'}} )


## item from financial statement
db.getCollection('universalData').find({ 'type1':'Financial Statements', 'type2':'balance_sheet', 'type3':'assets', 'period':'q', 'type5':'Total Assets', 'type6':'None', 'type7':'None'}).sort( {'type4':-1} )

## get an item from financial statements
db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements', 'type2':'income_statement', 'type3':'None', 'type4':2016, 'type5':'Sales/Revenue', 'type6':'None', 'type7':'None' } )

*fiscal_note*<br/>
db.getCollection('universalData').find({'ticker':'2333.HK', 'type1':'Financial Statements', 'type2':'balance_sheet', 'type3':'assets', 'type4':2016, 'type5':'_FISCAL_NOTE_' } )


