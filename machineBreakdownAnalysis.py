from datetime import date, timedelta

from dataAnalysis import getDateTimeDiff
from importer import *
from importer.fileImport import FileImporter

defaultDataTypes = {
    'machineId': int,
    'eventDateTime': safeDateTimeParse
}

fileImporter = FileImporter(f'{DATA_FILE_PATH}MachineBreakdownData_20201216_20201229.csv', defaultDataTypes=defaultDataTypes)
fileImporter.printRows(10)
# Group data by event description to determine unique event types (by looking at the unique keys in the grouped data)
eventDescriptionGroups = fileImporter.getGroupData([('eventDescription',)])

# Filter out data with no eventDescription
filteredEvents = [record for record in fileImporter.data if record['eventDescription']]
filteredEvents.sort(key=lambda record: record['eventDateTime'])

eventKeys = {
    # eventDescription: eventKey
    'Machine broke': 'brokeDateTime',
    'Mechanic started repairing machine': 'mechanicRepairingDateTime',
    'Machine is fixed': 'fixedDateTime'
}
eventRecordsByMachine = {}
for record in filteredEvents:
    machineId = record['machineId']
    eventKey = eventKeys[record['eventDescription']]
    newEventRecord = {}
    newEventRecord['machineId'] = machineId
    newEventRecord['machineType'] = record['machineType']
    newEventRecord[eventKey] = record['eventDateTime']
    if machineId not in eventRecordsByMachine:
        eventRecordsByMachine[machineId] = [newEventRecord]
    elif eventKey in eventRecordsByMachine[machineId][-1]:
        eventRecordsByMachine[machineId].append(newEventRecord)
    else:
        eventRecordsByMachine[machineId][-1][eventKey] = record['eventDateTime']

eventRecords = []
for records in eventRecordsByMachine.values():
    eventRecords.extend(records)

# Return False if an event key is missing or the events are not in the correct sequence
# Otherwise return True
def isGoodEventRecord(eventRecord):
    for eventKey in ('brokeDateTime', 'mechanicRepairingDateTime', 'fixedDateTime'):
        if eventKey not in eventRecord:
            print(f'Missing an eventKey for {eventRecord}')
            return False
    if ((eventRecord['brokeDateTime'] > eventRecord['mechanicRepairingDateTime'])
            or (eventRecord['mechanicRepairingDateTime'] > eventRecord['fixedDateTime'])):
        print(f'Event sequence out of order for {eventRecord}')
        return False
    return True

eventRecords = list(filter(isGoodEventRecord, eventRecords))

# Add the following values to each eventRecord
# 1) brokeDate - the date value from 'brokeDateTime'
# 2) brokeToMechanicMinutes - difference in minutes between 'brokeDateTime' and 'mechanicRepairingDateTime'
# 3) mechanicToFixedMinutes - difference in minutes between 'mechanicRepairingDateTime' and 'fixedDateTime'
# 4) brokeToFixedMinutes - difference in minutes between 'brokeDateTime' and 'fixedDateTime'
for record in eventRecords:
    brokeDateTime = record['brokeDateTime']
    mechanicRepairingDateTime = record['mechanicRepairingDateTime']
    fixedDateTime = record['fixedDateTime']
    record['brokeDate'] = brokeDateTime.date()
    record['brokeToMechanicMinutes'] = getDateTimeDiff(mechanicRepairingDateTime, brokeDateTime)
    record['mechanicToFixedMinutes'] = getDateTimeDiff(fixedDateTime, mechanicRepairingDateTime)
    record['brokeToFixedMinutes'] = getDateTimeDiff(fixedDateTime, brokeDateTime)

# Save the rawData for later to print to Excel and then set the fileImporter data to
# eventRecords so we can use the getGroupData method
rawData = fileImporter.data
fileImporter.data = eventRecords
# Group the eventRecords by machineType and brokeDate
# Don't forget that you only want the value of the dictionary. The key will be ('machineType', 'brokeDate')
machineTypeDateGroupEvents = fileImporter.getGroupData([('machineType', 'brokeDate')])[('machineType', 'brokeDate')]

dateHeaders = [None] + [date(2020, 12, 16) + timedelta(days=dayIdx) for dayIdx in range(14)]
machineTypes = {
    'Car door machine': [],
    'Car window machine': [],
    'Car body machine': [],
    'Car engine machine': [],
    'Car machine': [],
    'Paint machine': []
}
rows = ['brokeToMechanicMinutes', 'mechanicToFixedMinutes', 'brokeToFixedMinutes']

for machineType, values in machineTypes.items():
    """
    Create a new record for every value in rows
    The record should have the row value as the first item
    Every value after that should be a sum of the minutes for the row and date
    For example:
        ['brokeToMechanicMinutes', None, 345, 24, None, ...]
    Hint: The keys in machineTypeDateGroup events will be a tuple of (<machineType>, <brokeDate>). The
    value corresponding to the key will be a list of eventRecords. You can use the row value as the key
    for each eventRecord. For example if row = 'brokeToMechanicMinutes', you can access that value
    in each eventRecord using record[row].
    There should be 15 values for every new record - 1 for the row value and 14 for every date (12/16/2020 - 12/29/2020)
    Append the new record to values. Every values list should have three lists inside of it.
    One for each row value ('brokeToMechanicMinutes', 'mechanicToFixedMinutes', 'brokeToFixedMinutes')
    """
    for row in rows:
        newRecord = [row]
        for date in dateHeaders[1:]:
            machineTypeDateValues = machineTypeDateGroupEvents.get((machineType, date), None)
            if machineTypeDateValues is None:
                newRecord.append(None)
            else:
                sumOfMinutes = sum([value[row] for value in machineTypeDateValues])
                newRecord.append(sumOfMinutes)
        values.append(newRecord)

# Update sheets config to create a new worksheet for the data from each machine type
# The headers should be the same for every config - dateHeaders
sheetsConfig = [
    {'data': records, 'headers': dateHeaders, 'title': machineType}
    for machineType, records in machineTypes.items()
]

# Use fileImporter to write data to an output file called machineBreakdownAnalysis
fileImporter.writeExcelFile('machineBreakdownAnalysis', sheetsConfig=sheetsConfig)

print('Finished')