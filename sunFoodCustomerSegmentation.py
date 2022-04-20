from dataAnalysis import getAgeGroup
from importer import *
from importer.fileImport import FileImporter
from importer.groupStatistics import GroupStatistics, stringifyGroup

originalCustomerDataFileName = 'SunFoodShop_customers.csv'

def getSunFoodFileImporter(fileName, rowFilterFn=None):
    defaultDataTypes = {
        'isMarried': int,
        'isEmployed': int,
        'hasNewBaby': int,
        'age': int,
        'annualIncome': float,
        'childrenNum': int,
        'avgPurchaseAmount': float
    }

    return FileImporter(f'{DATA_FILE_PATH}{fileName}', defaultDataTypes=defaultDataTypes, rowFilterFn=rowFilterFn)

fileImporter = getSunFoodFileImporter(originalCustomerDataFileName)

def getBabySegmentData(fileImporter):
    groupedData = fileImporter.getGroupData([('hasNewBaby',),])

    hasNewBabySegments = groupedData[('hasNewBaby',)]
    babySegmentsStats = {groupKey: GroupStatistics(group) for groupKey, group in hasNewBabySegments.items()}
    babyAnalysisData = []

    for groupKey, groupStats in babySegmentsStats.items():
        stats = groupStats.calculatedStatistics
        newRecord = []
        newRecord.append(stringifyGroup(('hasNewBaby',), groupKey))  # Implement the stringifyGroup function
        newRecord.append((stats['customerKey'][groupStats.COUNT] / len(fileImporter.data)) * 100)
        newRecord.append(stats['customerKey'][groupStats.COUNT])
        newRecord.append(round(stats['avgPurchaseAmount'][groupStats.MEAN], 2))
        newRecord.append(round(stats['avgPurchaseAmount'][groupStats.MAX], 2))
        newRecord.append(round(stats['avgPurchaseAmount'][groupStats.MIN], 2))
        newRecord.append(stats['isEmployed'][groupStats.MEAN] * 100)
        newRecord.append(stats['age'][groupStats.MEAN])
        newRecord.append(round(stats['annualIncome'][groupStats.MEAN], 2))
        babyAnalysisData.append(newRecord)

    return babyAnalysisData

babyAnalysisData = getBabySegmentData(fileImporter)

groupedData = fileImporter.getGroupData([
    ('hasNewBaby',),
    ('sex', ('age', getAgeGroup)),
])
groupedSegmentStats = {}
for groupedDataKey, groupedSegments in groupedData.items():
    groupedSegmentStats[groupedDataKey] = {groupKey: GroupStatistics(group) for groupKey, group in groupedSegments.items()}

segmentationHeaders = ['group', 'customerCount', 'avgPurchasePrice']
segmentationAnalysisData = []

for groupedDataKey, segmentStats in groupedSegmentStats.items():
    for groupKey, groupStats in segmentStats.items():
        newRecord = []
        stats = groupStats.calculatedStatistics
        newRecord.append(stringifyGroup(groupedDataKey, groupKey))
        newRecord.append(stats['customerKey'][groupStats.COUNT])
        newRecord.append(round(stats['avgPurchaseAmount'][groupStats.MEAN], 2))
        segmentationAnalysisData.append(newRecord)

babySegmentHeaders = ['group', 'groupPct', 'count', 'avgPurchasePrice', 'maxPurchasePrice', 'minPurchasePrice', 'pctEmployed', 'avgAge', 'avgAnnualIncome']
sheetsConfig = [
    {'data': babyAnalysisData, 'headers': babySegmentHeaders, 'title': 'babyAnalysis'},
    {'data': segmentationAnalysisData, 'headers': segmentationHeaders, 'title': 'segmentationAnalysis'},
    {'title': 'rawData'},
]
fileImporter.writeExcelFile('sunFoodBabyAnalysis', sheetsConfig=sheetsConfig)
print('Finished')