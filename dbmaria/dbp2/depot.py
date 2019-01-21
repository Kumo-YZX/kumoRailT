#----------------------------------------------------------------#
# Module Name: Depot #
# Function: Define command to control items in DEPOT table. #
# Author: Kumo #
# Last Edit: Dec/13/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', '../dbmaria2.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self):
        dbBase.__init__(self, 'depot')

    def create(self, definitionFile='depot_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def insert(self, depotId, depotCn):
        """Insert item to the table.
           Parameter depotId is self-defined but less than 9999.
           Parameter depotCn must be in Han(Direct hanzi) format.
        """
        self.insertData({'depotId':depotId, 'depotCn':depotCn.encode('hex')})

    def insertDict(self, parameterDict):
        """Insert to table with parameter in json format.
        """
        self.insertData(parameterDict)

    def search(self, depotId=0):
        """Search for item in this table.
           Parameters are not essential.
           If provided, designed item will be returned, else it will return all items.
           Results is formatted in existence-result format with raw items.
        """
        if depotId:
            res = self.queryData([{'depotId':depotId}])
        else:
            res = self.queryData([])
        return len(res), res

    def delete(self, depotId=0):
        """Delete data.
           Parameter depotId are not essential.
           If provided, designated item will be deleted.
           If not provided, all items will be deleted.
        """
        if depotId:
            self.deleteData([{'depotId':depotId}])
        else:
            self.deleteData([])

def test():
    obj = table()
    obj.create()
    while(1):
        depotId = raw_input('depotId:')
        if int(depotId) == 9999:
            break
        depotCn = raw_input('depotCn:')
        obj.insert(int(depotId), depotCn)
    print 'INSERT DEPOT DONE'

if __name__ =='__main__':
    test()

