#---#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', 'dbmaria.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self, configFile = 'dbconfig.json'):
        dbBase.__init__(self, 'proxy', configFile)

    def create(self, definitionFile = 'proxy_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))
    
    def insertDict(self, paraDict):
        self.insertData(paraDict)

    def random(self, proxyType):
        res = self.searchRandom(proxyType, 1)
        return len(res), res

    def updateStatus(self, proxyId, connectTimes, failTimes):
        self.updateData({"connectTimes":connectTimes, "failTimes":failTimes},
                        [{"proxyId":{"judge":"=", "value":proxyId}}])

    def delete(self, proxyId):
        self.deleteData({"proxyId":{"judge":"=", "value":proxyId}})

    def verify(self, address, port):
        res = self.verifyExistence([{"address":{"judge":"=", "value":address}, "port":{"judge":"=", "value":port}}])
        return res

def test():
    obj = table()
    obj.create()


if __name__ == "__main__":
    test()

