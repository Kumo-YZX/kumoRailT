#--#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', 'dbmaria.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self, configFile = 'dbconfig.json'):
        dbBase.__init__(self, 'staInfo', configFile)

    def create(self, definitionFile='staInfo_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def updateAll(self):
        import urllib2
        siteUrl = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        rawData = urllib2.urlopen(siteUrl, timeout=5).read()
        rawData = rawData[21:-2]
        allStation = rawData.split('@')
        for everyStation in allStation:
            infoSplit = everyStation.split('|')
            self.insertData({"staCn": infoSplit[1].encode("hex"), "staTele": infoSplit[2], "staPy": infoSplit[4], "staNum":int(infoSplit[5])})
        return 1

    def insert(self, parameterDict):
        self.insertData(parameterDict)

    def delete(self, key='', value=''):
        if key == '':
            self.deleteData()
        else:
            self.deleteData([{key:{"judge":"=", "value":value}}])

        return 1

    def search(self, key='', value=''):
        if key == '':
            res = self.queryData()
        else:
            res = self.queryData([], [{key:{"judge":"=", "value":value}}])
        
        return len(res), res

    def verify(self, key, value):
        res = self.verifyExistence([{key:{"judge":"=", "value":value}}])
        return res

    def verifySpecial(self, staNum):
        res = self.verifyExistence([{'staNum':{'judge':'>=', 'value':staNum}}])
        return res


def initilize():
    tbObj = table()
    tbObj.create()
    tbObj.delete()
    tbObj.updateAll()

if __name__ == "__main__":
    initilize()