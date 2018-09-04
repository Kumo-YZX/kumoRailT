#---#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', 'dbmaria.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self, configFile = 'dbconfig.json'):
        dbBase.__init__(self, 'depot', configFile)

    def create(self, definitionFile='depot_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def insert(self, depotId, depotCn):
        self.insertData({'depotId':depotId, 'depotCn':depotCn.encode('hex')})

    def insertDict(self, parameterDict):
        self.insertData(parameterDict)

    def search(self, depotId=-1):
        if depotId < 0:
            res = self.queryData([])
        else:
            res = self.queryData([], [{'depotId':{'judge':'=', 'value':depotId}}])
        return len(res), res

    def delete(self, depotId=0):
        if depotId:
            self.deleteData([{'depotId':{'judge':'=', 'value':depotId}}])
        else:
            self.deleteData()

def test():
    obj = table()
    obj.create()
    while(1):
        depotId = raw_input('depotId:')
        if depotId == 9999:
            break
        depotCn = raw_input('depotCn:')
        obj.insert(int(depotId), depotCn)
    print 'INSERT DEPOT DONE'

if __name__ =='__main__':
    test()

