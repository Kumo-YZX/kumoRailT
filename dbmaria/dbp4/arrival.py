#----------------------------------------------------------------#
# Module Name: Arrival #
# Function: Recode a arrival in ARRIVAL table. #
# Author: Kumo #
# Last Edit: Dec/24/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', '../dbmaria2.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self):
        dbBase.__init__(self, 'arrival')

    def create(self, definitionFile='arrival_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def insert(self, trainStr, staTele, staRank, arrTime, arrDate, depTime, depDate):
        """Insert a arrival to the table.
           All parameters are required.
        """
        self.insertData({"trainStr":trainStr,
                         "staTele":staTele,
                         "staRank":staRank,
                         "arrTime":arrTime,
                         "arrDate":arrDate,
                         "depTime":depTime,
                         "depDate":depDate
                         })

    def insertDict(self, paraDict):
        """Insert data to table directly, using dict directly.
        """
        self.insertData(paraDict)

    def search(self, trainStr=None, staTele=None):
        """Search for items by its trainStr or staTele.
           You must choose one or more condition(s) from trainStr and staTele.
        """
        conditionDict = {}
        if trainStr is not None:
            conditionDict['trainStr'] = {'judge':'=', 'value':trainStr}
        if staTele is not None:
            conditionDict['staTele'] = {'judge':'=', 'value':staTele}

        if len(conditionDict):
            res = self.queryData([conditionDict])
        else:
            res = self.queryData()

        return len(res), res

    def searchById(self, arrivalId):
        res = self.queryData([{"arrivalId":{"judge":"=", "value":arrivalId}}])
        return len(res), res

    def searchLast(self):
        """Search for the last item in arrival table.
           Items is sorted by arrivalID.
           NO parameters required.
        """
        res = self.queryData([], orderFactor={'arrivalId':'DESC'}, amountLimit=1)
        return len(res), res

    def delete(self, trainStr=None):
        """Delete a item/items.
           Parameter are not essential, causing all items deleted.
           If provided, the item that trainStr mached will be deleted.
        """
        if trainStr is None:
            self.deleteData()
        else:
            self.deleteData([{"trainStr":{"judge":"=", "value":trainStr}}])

        return 1

    def verifyArrival(self, trainStr=None):
        """Verify the existence of a item.
           Parameter are not essential, changing the function to void-judgement.
           A json structure like [{'COUNT(1)':amount}] will be returned.
        """
        if trainStr is None:
            res = self.verifyExistence([])
        else:
            res = self.verifyExistence([{"trainStr":{"judge":"=", "value":trainStr}}])
        return res[0]['COUNT(1)']

    def searchJoin(self):
        """
        """
        res = self.queryJoin()
        return res

def init():
    obj = table()
    obj.create()

if __name__ == "__main__":
    init()