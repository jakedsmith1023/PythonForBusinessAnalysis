from dataAnalysis import getAgeGroup
from importer import *
from importer.fileImport import FileImporter
from importer.groupStatistics import GroupStatistics

defaultDataTypes = {
    'purchaseDateTime': safeDateTimeParse,
    'unitPrice': float,
    'unitCost': float,
    'quantity': int,
    'discountPct': float
}

fileImporter = FileImporter(f'{DATA_FILE_PATH}SalesData_HighArcticWool_2020.csv', defaultDataTypes=defaultDataTypes)
salesData = fileImporter.data
customerData = FileImporter(f'{DATA_FILE_PATH}CustomerData_HighArcticWool_2020.csv', defaultDataTypes={'age': int}).data
customerData = {record['customerKey']: record for record in customerData}

# Copy and extend 'customerKey', and 'age' column onto salesData
for sale in salesData:
    customer = customerData.get(sale['customerKey'], None)
    if not customer:
        raise ValueError('Customer doesn\'t exist')
    sale['age'] = customer['age']
    sale['unitDiscountPrice'] = sale['unitPrice'] * (1 - sale['discountPct'])
    sale['unitProfit'] = sale['unitDiscountPrice'] - sale['unitCost']
    sale['totalPrice'] = sale['unitPrice'] * sale['quantity']
    sale['totalProfit'] = sale['unitProfit'] * sale['quantity']

ageGroupSalesData = fileImporter.getGroupData([(('age', getAgeGroup),)], data=salesData, isFlat=True)[0]

ageGroupSalesStatistics = {groupKey: GroupStatistics(group) for groupKey, group in ageGroupSalesData.items()}

headers = ['ageGroup', 'totalProfit', 'avgProfit']
records = []
for (ageGroup,), groupStats in ageGroupSalesStatistics.items():
    newRecord = [ageGroup]
    newRecord.append(groupStats.calculatedStatistics['totalProfit'][GroupStatistics.SUM])
    newRecord.append(groupStats.calculatedStatistics['totalProfit'][GroupStatistics.MEAN])
    records.append(newRecord)

sheetsConfig = [
    {'data': records, 'headers': headers, 'title': 'ageGroups'}
]

fileImporter.writeExcelFile('highArcticAgeAnalysis', sheetsConfig=sheetsConfig)

print('Finished')