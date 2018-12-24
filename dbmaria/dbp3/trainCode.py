#----------------------------------------------------------------#
# Module Name: TrainCode #
# Function: Define commands to control items in trainCode table. TrainCodes follow trains. #
# Author: Kumo #
# Last Edit: Dec/14/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', '../dbmaria2.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self):
        dbBase.__init__(self, 'trainCode')

    def create(self, definitionFile='trainCode_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def insert(self, trainStr, departDate, trainCode):
        """Insert a trainCode data to database.
           The departDate parameter must be in YYYY-MM-DD fromat.
           The trainStr and trainCode parameter must be strings with length of 8 and 12.
        """
        if not(self.verify(trainStr, departDate)[0]['COUNT(1)']):
            self.insertData({"trainStr":trainStr, "departDate":departDate, "trainCode":trainCode})

    def search(self, trainStr, depDate=''):
        """Search for a data with particular trainStr.
           The depDate parameter is not essential.
           If provided, result will only contain data behind that date.
           It bust must be in YYYY-MM-DD format.
           Return value is in L(ength)/R(esult) formet.
        """
        if depDate == '':
            res = self.queryData([{"trainStr":trainStr}])
        else:
            res = self.queryData([{"trainStr":trainStr,
                                   "departDate":{"judge":">=", "value":depDate}}])
        return len(res), res

    def insertDict(self, parameterDict):
        self.insertData(parameterDict)

    def searchAll(self):
        """Search for all the data in this table.
           Not recommand to use.
        """
        res = self.queryData([])
        return len(res), res

    def delete(self, key=None, value=None):
        """Delete items in this table.
           Parameters are not required, and all items will be deleted.
           If provided, only the item designated will be deleted. 
        """
        if key is None:
            self.deleteData([])
        else:
            self.deleteData([{key:value}])

    def verify(self, trainStr, date):
        """Count the data that matchs with particular trainStr and date.
        """
        res = self.verifyExistence([{"trainStr":trainStr, 
                                     "departDate":date}])
        return res[0]['COUNT(1)']

def initalize():
    obj = table()
    obj.create()

if __name__ == "__main__":
    initalize()


