from importer import *
from importer.fileImport import FileImporter

defaultHeaders = {
    0: 'Name',
    'Height (Inches)': 'Height_Inches',
    'Marital status': 'Marital_Status',
    'Height %': 'Height_Percentile'
}

defaultDataTypes = {
    'Age': int,
    'Height_Inches': int,
    'Employment_date': safeDateTimeParse,
    'Height_Percentile': parsePercentageString
}

fileImporter = FileImporter(f'{DATA_FILE_PATH}DemographicSampleMoreData.xlsx', defaultHeaders=defaultHeaders, defaultDataTypes=defaultDataTypes, rowDataType=ROW_TYPE_LIST)
fileImporter.printRows(5)
fileImporter.writeFile(FILE_TYPE_XLS, 'demographicProcessed')