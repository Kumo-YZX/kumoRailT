#---#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', 'dbmaria.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self, configFile = 'dbconfig.json'):
        dbBase.__init__(self, 'trainCode', configFile)

    def create(self, definitionFile='trainCode_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def insert(self, trainStr, departDate, trainCode):
        if not(self.verify(trainStr, departDate)):
            self.insertData({"trainStr":trainStr, "departDate":departDate, "trainCode":trainCode})

    def search(self, trainStr, depDate=''):
        if depDate == '':
            res = self.queryData([], [{"trainStr":{"judge":"=", "value":trainStr}}])
        else:
            res = self.queryData([], [{"trainStr":{"judge":"=", "value":trainStr},
                                 "departDate":{"judge":">=", "value":depDate}}])

        if len(res):
            return 1, res
        else:
            return 0, []

    def delete(self, key='', value=''):
        if key == '':
            self.deleteData()
        else:
            self.deleteData([{key:{"judge":"=", "value":value}}])

    def verify(self, trainStr, date):
        res = self.verifyExistence([{"trainStr":{"judge":"=", "value":trainStr}, "departDate":{"judge":"=", "value":date}}])
        return res

def initalize():
    obj = table()
    obj.create()

if __name__ == "__main__":
    initalize()


