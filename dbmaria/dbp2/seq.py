#----------------------------------------------------------------#
# Module Name: Seq #
# Function: Define commands to control items in SEQ table. Seqs follow depots. #
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
        dbBase.__init__(self, 'seq')

    def create(self, definitionFile='seq_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def verify(self, key, value):
        """Verify the existence of an item.
           Parameters are all required and should mark data.
        """
        res = self.verifyExistence([{key:value}])
        return res[0]['COUNT(1)']

    def importAll(self, seqFile='seq_data.json'):
        """Import data from specified file.
           Repeated value will not be writed.
           Parameter filename are not essential, or default value will be used.
        """
        with open(seqFile) as fi:
            seqList = json.load(fi)

        for everySeq in seqList:
            if everySeq['sequence'] == "":
                everySeq['sequence'] = 0
            if self.verify('seqId', everySeq['sequence']):
                print 'Info: seq already exists'
            else:
                if everySeq['staffDep'] == 0:
                    everySeq['staffDep'] = 127
                if everySeq['vehicleDep'] == 0:
                    everySeq['vehicleDep'] = 127
                self.insertData({"seqId":everySeq['sequence'],
                                "staff":everySeq['staffDep'],
                                "depot":everySeq['vehicleDep'],
                                "emuType":everySeq['emuType'].encode('utf8').encode('hex'),
                                "remark":everySeq['remark'].encode('utf8').encode('hex')})

    def insertDict(self, parameterDict):
        """Insert to table with value in json format.
        """
        self.insertData(parameterDict)

# Edited Dec/14/2018: Change Meaningless defalue value to NONE #
    def delete(self, key=None, value=None):
        """Delete an item.
           Parameters are not essential, causing all data deleted.
           If provided, designed item will be deleted.
        """
        if key is None:
            self.deleteData([])
        else:
            self.deleteData([{key:value}])

    def search(self, key=None, value=None):
        """Search for item(s).
           Parameters are not essential, and all items will be returned.
           If provided, the item they marked will be returned.
           Results is formatted in existence-result value.
        """
        if key is None:
            res = self.queryData([])
        else:
            res = self.queryData([{key:value}])
        
        return len(res), res

    # def update(self, key, value):
    #     pass

def initalize():
    seqObj = table()
    seqObj.create()
    seqObj.importAll()

if __name__ == "__main__":
    initalize()

