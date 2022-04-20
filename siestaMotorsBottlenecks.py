from dataAnalysis import getDateTimeDiff, TIME_AGG_MINUTES
from importer import *
from importer.fileImport import FileImporter
from importer.groupStatistics import GroupStatistics, stringifyGroup

defaultDataTypes = {
    'partId': int,
    'machineId': int,
    'processingStartTime': safeDateTimeParse,
    'processingEndTime': safeDateTimeParse,
    'inputPartId': int,
    'inputPartReadyTime': safeDateTimeParse
}

defaultHeaders = {
    7: 'inputPartName',
    'subPartReadyTime': 'inputPartReadyTime'
}

fileImporter = FileImporter(f'{DATA_FILE_PATH}CarProcessingData_20201216_20201229.csv',
                            defaultHeaders=defaultHeaders, defaultDataTypes=defaultDataTypes)

newDataHeaders = ['partId', 'partName', 'machineId', 'machineType', 'processingStartTime', 'processingEndTime']

aggregatedCarData = {}
for record in fileImporter.data:
    newRecord = aggregatedCarData.get(record['partId'], None)
    if not newRecord:
        newRecord = {header: record[header] for header in newDataHeaders}
        newRecord['processingMinutes'] = getDateTimeDiff(record['processingEndTime'], record['processingStartTime'])
        newRecord['processingStartDate'] = record['processingStartTime'].date()
        newRecord['inputPartIds'] = []
        newRecord['readyProcessingStartTime'] = None
        if record['inputPartId']:
            newRecord['inputPartIds'].append(record['inputPartId'])
            newRecord['readyProcessingStartTime'] = record['inputPartReadyTime']
        aggregatedCarData[record['partId']] = newRecord
    else:
        if record['inputPartId']:
            newRecord['inputPartIds'].append(record['inputPartId'])
            if record['inputPartReadyTime'] > newRecord['readyProcessingStartTime']:
                newRecord['readyProcessingStartTime'] = record['inputPartReadyTime']

for record in aggregatedCarData.values():
    record['waitTimeMinutes'] = getDateTimeDiff(record['processingStartTime'], record['readyProcessingStartTime'])
    record['inputPartIds'] = tuple(record['inputPartIds'])

fileImporter.data = list(aggregatedCarData.values())
carPartDataGroups = fileImporter.getGroupData([('partName', 'processingStartDate')])[('partName',
                                                                                         'processingStartDate')]


carPartDateGroups = {groupKey: GroupStatistics(group) for groupKey, group in carPartDataGroups.items()}

headers = ['partName', 'processingStartDate', 'processingTimeMin', 'processingTimeMax', 'processingTimeAvg',
           'processingTimeStdDev', 'waitTimeMin', 'waitTimeMax', 'waitTimeAvg', 'waitTimeStdDev']

carPartDateOutputData =[]
for groupKey, groupStats in carPartDateGroups.items():
    newRecord = []
    newRecord.append(groupKey[0])
    newRecord.append(groupKey[1])

    stats = groupStats.calculatedStatistics
    processingTimeStats = stats['processingMinutes']
    waitTimeStats = stats['waitTimeMinutes']
    for timeStats in (processingTimeStats, waitTimeStats):
        for metric in (groupStats.MIN, groupStats.MAX, groupStats.MEAN, groupStats.STD_DEVIATION):
            newRecord.append(timeStats[metric])
    carPartDateOutputData.append(newRecord)

def isPartInProcess(record):
    if not record['processingStartTime'] or not record['processingEndTime']:
        return False
    targetDateTime = record['processingStartTime'].replace(hour=23, minute=0, second=0, microsecond=0)
    return record['processingStartTime'] <= targetDateTime and record['processingEndTime'] >= targetDateTime

machineDataGroups = fileImporter.getGroupData([('machineId', 'machineType', 'processingStartDate')],
                                                  filterFn=isPartInProcess)[('machineId', 'machineType',
                                                                             'processingStartDate')]
partsProcessingHeaders = ['machineName', 'date', 'partsInProcess']
partsInProcessRecords = []
for groupKey, partsList in machineDataGroups.items():
    newRecord = []
    newRecord.append(f'{groupKey[1]} ({groupKey[0]})')
    newRecord.append(groupKey[2])
    newRecord.append(len(partsList))
    partsInProcessRecords.append(newRecord)


sheetsConfig = [
    {'data': carPartDateOutputData, 'headers': headers, 'title': 'partProcessAnalysis'},
    {'data': partsInProcessRecords, 'headers': partsProcessingHeaders, 'title': 'machineThroughput'}
]

fileImporter.writeExcelFile('carPartProcessingAnalysis', sheetsConfig=sheetsConfig)

print('Finished')
