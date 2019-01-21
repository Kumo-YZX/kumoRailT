#----------------------------------------------------------------#
# Module Name:StaInfo #
# Function: Define database command to control items in STAINFO table. #
# Author: Kumo #
# Last Edit: Dec/12/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', '../dbmaria2.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self):
        dbBase.__init__(self, 'staInfo')

    def create(self, definitionFile='staInfo_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def updateAll(self):
        """Fill the table with newest data.
           You need to delete old data manually.
           No parameters required.
        """
        import urllib2
        siteUrl = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        rawData = urllib2.urlopen(siteUrl, timeout=5).read()
        rawData = rawData[21:-2]
        allStation = rawData.split('@')
        for everyStation in allStation:
            infoSplit = everyStation.split('|')
            self.insertData({"staCn": infoSplit[1].encode("hex"), "staTele": infoSplit[2], "staPy": infoSplit[4], "staNum":int(infoSplit[5])})

    def insert(self, parameterDict):
        """Insert data to table manually.
           Parameter: parameterDict must be formed in formatted form.
        """
        self.insertData(parameterDict)

    def delete(self, key=None, value=None):
        """Delete data.
           Parameters are not essential.
           If provded, they must be in key-value format that maches table items.
           If not provided, all data in this table will be deleted.
        """
        if key is None:
            self.deleteData()
        else:
            self.deleteData([{key:value}])

    def search(self, key=None, value=None):
        """Search for data in this table.
           Parameters are not essential.
           If provided, they must be in key-value format that maches table items.
           If not provided, all data will be returned.
           Return value will be in existence-result format with raw items.
        """
        if key is None:
            res = self.queryData()
        else:
            res = self.queryData([{key:value}])
        
        return len(res), res

    def verify(self, key, value):
        """Verify the existence of specified data.
           Parameters: key value are essential.
           The result means both the existence and the amount.
        """
        res = self.verifyExistence([{key:value}])
        return res

    def updateSele(self, staTele, status=0):
        """Mark the station as special.
           Parameter is the staTele of the item.
           Nothing will be returned.
        """
        self.updateData({"seleSta":status},
                        [{"staTele":staTele}])

    def verifySpecial(self, staNum):
        """Verify the existence of marked special data.
           Amount of this stations(a number) will be returned.
        """
        res = self.verifyExistence([{'staNum':{'judge':'>=', 'value':staNum}}])
        return res[0]['COUNT(1)']

if __name__ == "__main__":
    import sys
    obj = table()
    if sys.argv[1] == 'cre':
        obj.create()
    elif sys.argv[1] == 'upd':
        obj.updateAll()
    elif sys.argv[1] == 'del':
        obj.delete()
    else:
        print 'WHAT DO YOU WANT TO DO?'