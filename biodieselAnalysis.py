from importer import *
from importer.fileImport import FileImporter

def getYearInt(val):
    return int(val[:4])

defaultHeaders = {
    'Marketing year1': 'Marketing_Start_Year',
    'Beginning stocks2': 'Beginning_Stocks',
    'Ending stocks': 'Ending_Stocks',
    7: 'Total2'
}

defaultDataTypes = {
    'Marketing_Start_Year': getYearInt,
    'Beginning_Stocks': parseIntegerString,
    'Production': parseIntegerString,
    'Imports': parseIntegerString,
    'Total': parseIntegerString,
    'Domestic': parseIntegerString,
    'Exports': parseIntegerString,
    'Total2': parseIntegerString,
    'Ending_Stocks': parseIntegerString
}

fileImporter = FileImporter(f'{DATA_FILE_PATH}BiodieselDataChallenge.csv', defaultHeaders=defaultHeaders,
                            defaultDataTypes=defaultDataTypes, rowLimit=18)
fileImporter.printRows(5)
fileImporter.writeFile(FILE_TYPE_CSV, 'biodieselProcessed')