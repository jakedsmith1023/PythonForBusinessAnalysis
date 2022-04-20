from datetime import datetime
from dateutil.parser import parse

DATA_FILE_PATH = '/Users/jakesmith/PycharmProjects/udemy_Python4BusinessAnalysisandExcel/dataFiles/'
DATA_FILE_OUTPUT_PATH = '/Users/jakesmith/PycharmProjects/udemy_Python4BusinessAnalysisandExcel/outputFiles/'

ROW_TYPE_DICT = 'dict'
ROW_TYPE_LIST = 'list'
ROW_TYPE_TUPLE = 'tuple'

FILE_TYPE_CSV = 'csv'
FILE_TYPE_XLS = 'xls'

DEFAULT_NONE_STRINGS = ('null', 'na', 'n/a')


def safeDateTimeParse(val):
    if isinstance(val, datetime):
        return val
    return parse(val)

def parsePercentageString(val):
    return float(val.replace('%', ''))

def parseIntegerString(val):
    return int(val.replace(',', ''))