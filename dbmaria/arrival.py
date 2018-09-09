#---#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', 'dbmaria.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self):
        dbBase.__init__(self, 'arrival')

    def create(self, definitionFile='arrival_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def insert(self, trainStr, staTele, staRank, arrTime, arrDate, depTime, depDate):
        self.insertData({"trainStr":trainStr,
                         "staTele":staTele,
                         "staRank":staRank,
                         "arrTime":arrTime,
                         "arrDate":arrDate,
                         "depTime":depTime,
                         "depDate":depDate
                         })

    def insertDict(self, paraDict):
        self.insertData(paraDict)

    def search(self, trainStr=None, staTele=None):
        conditionDict = {}
        if trainStr is not None:
            conditionDict['trainStr'] = {'judge':'=', 'value':trainStr}
        if staTele is not None:
            conditionDict['staTele'] = {'judge':'=', 'value':staTele}

        if len(conditionDict):
            res = self.queryData([], [conditionDict])
        else:
            res = self.queryData()

        return len(res), res

    def searchById(self, arrivalId):
        res = self.queryData([], [{"arrivalId":{"judge":"=", "value":arrivalId}}])
        return len(res), res

    def searchLast(self):
        res = self.queryData([], [], {'variable':'arrivalId', 'desc':True, 'amount':1})
        return len(res), res

    def delete(self, trainStr=''):
        if trainStr == '':
            self.deleteData()
        else:
            self.deleteData([{"trainStr":{"judge":"=", "value":trainStr}}])

        return 1

    def verifyArrival(self, trainStr=''):
        if trainStr == '':
            res = self.verifyExistence([])
        else:
            res = self.verifyExistence([{"trainStr":{"judge":"=", "value":trainStr}}])
        return res

    def searchJoin(self):
        res = self.queryJoin()
        return res

def test():
    obj = table()
    obj.create()

if __name__ == "__main__":
    test()