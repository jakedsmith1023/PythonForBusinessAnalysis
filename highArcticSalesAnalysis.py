from dataAnalysis import DATE_AGG_QUARTERS, DATE_AGG_MONTHS, getDateAgg
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

processedData = fileImporter.data
for record in processedData:
    record['unitDiscountPrice'] = record['unitPrice'] * (1 - record['discountPct'])
    record['unitProfit'] = record['unitDiscountPrice'] - record['unitCost']
    record['totalPrice'] = record['unitDiscountPrice'] * record['quantity']
    record['totalProfit'] = record['unitProfit'] * record['quantity']

purchaseDateGroup = fileImporter.getGroupData([(('purchaseDateTime', getDateAgg), 'productName')], data=processedData, isFlat=True)

getMonth = lambda record: getDateAgg(record, dateAgg=DATE_AGG_MONTHS)
getQuarter = lambda record: getDateAgg(record, dateAgg=DATE_AGG_QUARTERS)

purchaseMonthGroup = fileImporter.getGroupData([(('purchaseDateTime', getMonth), 'productName')], data=processedData, isFlat=True)
purchaseQuarterGroup = fileImporter.getGroupData([(('purchaseDateTime', getQuarter), 'productName')], data=processedData, isFlat=True)

seasonalityGroupStatistics = {
    'date': {groupKey: GroupStatistics(group) for groupKey, group in purchaseDateGroup[0].items()},
    'month': {groupKey: GroupStatistics(group) for groupKey, group in purchaseMonthGroup[0].items()},
    'quarter': {groupKey: GroupStatistics(group) for groupKey, group in purchaseQuarterGroup[0].items()}
}

metrics = ['totalPrice', 'totalProfit', 'quantity']
productLines = ['Mountain socks', 'Storm surge jacket', 'Aspen long sleeve shirt', 'Pine short sleeve shirt']
headers = ['dateCategory'] + metrics

seasonalityProductGroups = {}
for product in productLines:
    for seasonalityGroup in seasonalityGroupStatistics:
        seasonalityProductGroups[(product, seasonalityGroup)] = []

for (product, seasonalityGroup), records in seasonalityProductGroups.items():
    groupStatistics = seasonalityGroupStatistics[seasonalityGroup]
    for (dateAgg, specificProduct), statistics in groupStatistics.items():
        if product == specificProduct:
            newRecord = [dateAgg]
            calculatedStats = statistics.calculatedStatistics
            for metric in metrics:
                newRecord.append(calculatedStats[metric]['sum'])
            records.append(newRecord)

sheetsConfig = [
    {'data': records, 'headers': headers, 'title': f'{product}-{seasonalityGroup}'}
    for (product, seasonalityGroup), records in seasonalityProductGroups.items()
]

fileImporter.writeExcelFile('highArcticSeasonalityAnalysis', sheetsConfig=sheetsConfig)

print('Finished')