from dataAnalysis.sunFoodCustomerSegmentation import getBabySegmentData, getSunFoodFileImporter, originalCustomerDataFileName

# 6 month advertising campaign
# 12 months purchasing baby items
# Is the cost of the advertising campaign worth it based on expected customer value?

# Advertising campaign assumptions
# Rates by month - assumes that we continue acquiring customers one month after campaign ends
BABY_CUSTOMER_ACQUISITION_RATES = [0.4, 0.5, 0.5, 0.6, 0.8, 0.8, 0.5]
# Assumes that after 12 months customers will no longer purchase baby items
BABY_CUSTOMER_ATTRITION_RATES = [0, 0.08, 0.08, 0.08, 0.04, 0.04, 0.04, 0.04, 0.02, 0.02, 0.02, 0.02]
BABY_CUSTOMER_SPEND_MONTHS = 12
BABY_CUSTOMER_AD_COST = 10000

"""
Marketing campaign example customer revenue

Month | Month 1 customers | Month 2 customers | Month 3 customers |
1     | 10000             | 0                 | 0                 |
2     | 10000             | 10000             | 0                 |
3     | 10000             | 10000             | 10000             |
4     | 10000             | 10000             | 10000             |
5     | 10000             | 10000             | 10000             |
6     | 10000             | 10000             | 10000             |
"""

"""
Update this function to return a tuple with (customers, customerSpend)
Hint: Make use of most of the code from lines 34-37
"""
def getCustomersAndSpend(fileName, rowFilterFn):
    fileImporter = getSunFoodFileImporter(fileName, rowFilterFn=rowFilterFn)
    customersWithBaby = fileImporter.data
    customerSpend = sum([customer['avgPurchaseAmount'] for customer in customersWithBaby])
    return customersWithBaby, customerSpend, fileImporter

prePromoBabyCustomers, prePromoTotalSpend, fileImporter = getCustomersAndSpend(originalCustomerDataFileName, lambda row: bool(row['hasNewBaby']))
prePromoCustomerKeys = [customer['customerKey'] for customer in prePromoBabyCustomers]

"""
Update this function to return True if a customer has a new baby and
the customerKey is not in the pre promo customer keys (meaning this is a new customer)
"""
def isNewPromoCustomer(row):
    return row['hasNewBaby'] and row['customerKey'] not in prePromoCustomerKeys

aprilBabyCustomers, aprilTotalSpend, _ = getCustomersAndSpend('SunFoodShop_MarketingPromo_2021_Apr.csv', isNewPromoCustomer)

def getMarketingStats(baseCustomerCount, expectedMonthlySpend):
    totalMonthlyRevenue = []
    totalMonthlyCustomers = []
    for monthOffset, customerAcquisitionRate in enumerate(BABY_CUSTOMER_ACQUISITION_RATES):
        newCustomers = round(baseCustomerCount * customerAcquisitionRate)
        for month in range(12):
            currentMonth = monthOffset + month
            monthlyRevenue = newCustomers * expectedMonthlySpend
            try:
                totalMonthlyRevenue[currentMonth] += monthlyRevenue
            except IndexError:
                totalMonthlyRevenue.append(monthlyRevenue)

            attritionRate = BABY_CUSTOMER_ATTRITION_RATES[month]
            newCustomers = round(newCustomers * (1 - attritionRate))
            try:
                totalMonthlyCustomers[currentMonth] += newCustomers
            except IndexError:
                totalMonthlyCustomers.append(newCustomers)

    return totalMonthlyRevenue, totalMonthlyCustomers

totalMonthlyBabyRev, totalMonthlyBabyCustomers = getMarketingStats(len(prePromoBabyCustomers), prePromoTotalSpend / len(prePromoBabyCustomers))
roiHeaders = ['metric'] + [f'Month {idx + 1}' for idx in range(len(totalMonthlyBabyRev))] + ['Total']
roiData = []
for metricName, metricValues in (('Revenue', totalMonthlyBabyRev), ('New customers', totalMonthlyBabyCustomers)):
    roiData.append([metricName] + metricValues + [sum(metricValues)])

roiData.append([])
roiData.append([])
roiData.append(['Market promo cost', 'Total revenue', 'Roi (nominal)', 'Roi (pct)'])
expectedTotalRev = sum(totalMonthlyBabyRev)
nominalRoi = expectedTotalRev - BABY_CUSTOMER_AD_COST
roiData.append([BABY_CUSTOMER_AD_COST, expectedTotalRev, nominalRoi, (nominalRoi / BABY_CUSTOMER_AD_COST) * 100])

actualVsExpectedHeaders = ['metric', 'actual', 'expected', 'diff']
actualVsExpectedData = []
"""
Complete the rest of the two lists below based on the header values. The expected values
should be in the fourth month (index 3) of a list.
"""
actualVsExpectedData.append(['customers', len(aprilBabyCustomers), totalMonthlyBabyCustomers[3], len(aprilBabyCustomers) - totalMonthlyBabyCustomers[3]])
actualVsExpectedData.append(['revenue', aprilTotalSpend, totalMonthlyBabyRev[3], aprilTotalSpend - totalMonthlyBabyRev[3]])


sheetsConfig = [
    {'data': roiData, 'headers': roiHeaders, 'title': 'marketingBabyRoi'},
    {'data': actualVsExpectedData, 'headers': actualVsExpectedHeaders, 'title': 'month4ActualVsExpected'}
]
fileImporter.writeExcelFile('sunFoodMarketingRoiActual', sheetsConfig=sheetsConfig)

print('Finished')