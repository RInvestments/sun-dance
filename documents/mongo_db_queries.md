### Find 
db.getCollection('universalData').find({'type1':'Ownership', 'type2':'Institutional Investor','type3': /Sachs/, 'type4': 'Change In Shares'})

## Sort by Revenues
db.universalData.find({  'industry':'Technology', 'type1':'Profile', 'type2':'Company Info', 'type3':'Sales or Revenue'} ).sort( {'val':-1} )


## Aggregate


## Aggregate and match
db.getCollection('universalData').aggregate(  {$match:{'industry':'Automotive'}}, {$group: {_id:'$sector'}} )


## item from financial statement
db.getCollection('universalData').find({ 'type1':'Financial Statements', 'type2':'balance_sheet', 'type3':'assets', 'period':'q', 'type5':'Total Assets', 'type6':'None', 'type7':'None'}).sort( {'type4':-1} )
