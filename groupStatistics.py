from copy import deepcopy
from datetime import date, datetime
from statistics import stdev


def stringifyGroup(grouping, groupKey):
    """ Get a concatenated string of all pairs of grouping and groupKey variables
    :param tuple grouping: The names of the columns used for the grouping
    :param tuple groupKey: The values used in the grouping
    Example:
        grouping = ('hasNewBaby', 'educationLevel')
        groupKey = (0, 'College')
        returns (string): 'hasNewBaby: 0, educationLevel: College'
    """
    groupedVals = []
    for groupName, groupVal in zip(grouping, groupKey):
        groupedVals.append(f'{groupName}: {groupVal}')

    return ', '.join(groupedVals)


class GroupStatistics:

    # Aggregate level calculations
    MEAN = 'mean'
    PCT_UNIQUE = 'pctUnique'
    STD_DEVIATION = 'stdDeviation'

    # Record level calcultions
    MAX = 'max'
    MIN = 'min'
    SUM ='sum'
    COUNT = 'count'
    COUNT_NOT_NULL = 'countNotNull'
    COUNT_UNIQUE = 'countUnique'

    def __init__(self, groupData, headers=None):
        self.groupData = groupData if isinstance(groupData[0], dict) else {key: val for key, val in zip(headers, groupData)}
        self.setStartingStats()

        for record in self.groupData:
            for columnKey, value in record.items():
                self.calculateRecordStats(columnKey, value)

        for stats in self.calculatedStatistics.values():
            self.calculateAggStats(stats)

        for columnKey, stats in self.calculatedStatistics.items():
            if stats[self.MEAN]:
                columnData = [record[columnKey] for record in self.groupData if record[columnKey] is not None]
                stats[self.STD_DEVIATION] = stdev(columnData)

    def setStartingStats(self):
        statsTemplateDict = {
            self.MEAN: None,
            self.PCT_UNIQUE: {},
            self.STD_DEVIATION: None,
            self.MAX: None,
            self.MIN: None,
            self.SUM: None,
            self.COUNT: 0,
            self.COUNT_NOT_NULL: 0,
            self.COUNT_UNIQUE: {}
        }
        self.calculatedStatistics = {}

        for columnKey, value in self.groupData[0].items():
            self.calculatedStatistics[columnKey] = deepcopy(statsTemplateDict)

    def calculateRecordStats(self, columnKey, value):
        stats = self.calculatedStatistics[columnKey]
        self.calculateCount(stats)
        self.calculateCountNotNull(stats, value)
        self.calculateCountUnique(stats, value)
        self.calculateSum(stats, value)
        self.calculateMin(stats, value)
        self.calculateMax(stats, value)

    def calculateAggStats(self, stats):
        self.calculateMean(stats)
        self.calculatePctUnique(stats)

    def calculateCount(self, stats):
        stats[self.COUNT] += 1

    def calculateCountNotNull(self, stats, value):
        if value is not None:
            stats[self.COUNT_NOT_NULL] += 1

    def calculateCountUnique(self, stats, value):
        uniqueItems = stats[self.COUNT_UNIQUE]
        if value in uniqueItems:
            uniqueItems[value] += 1
        else:
            uniqueItems[value] = 1

    def calculateSum(self, stats, value):
        if isinstance(value, (int, float)):
            if stats[self.SUM] is None:
                stats[self.SUM] = value
            else:
                stats[self.SUM] += value

    def calculateMin(self, stats, value):
        if isinstance(value, (int, float, date, datetime)):
            if stats[self.MIN] is None:
                stats[self.MIN] = value
            elif value < stats[self.MIN]:
                stats[self.MIN] = value

    def calculateMax(self, stats, value):
        if isinstance(value, (int, float, date, datetime)):
            if stats[self.MAX] is None:
                stats[self.MAX] = value
            elif value > stats[self.MAX]:
                stats[self.MAX] = value

    def calculateMean(self, stats):
        try:
            if stats[self.SUM] is not None:
                stats[self.MEAN] = stats[self.SUM] / stats[self.COUNT_NOT_NULL]
        except ZeroDivisionError:
            pass

    def calculatePctUnique(self, stats):
        for uniqueVal, count in stats[self.COUNT_UNIQUE].items():
            stats[self.PCT_UNIQUE][uniqueVal] = (count / stats[self.COUNT]) * 100