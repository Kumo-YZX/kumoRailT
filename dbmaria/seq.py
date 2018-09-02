#---#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', 'dbmaria.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self, configFile = 'dbconfig.json'):
        dbBase.__init__(self, 'seq', configFile)

    def create(self, definitionFile='seq_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def verify(self, key, value):
        res = self.verifyExistence([{key:{"judge":"=", "value":value}}])
        return res

    def importAll(self, seqFile='seq_data.json'):
        with open(seqFile) as fi:
            seqList = json.load(fi)

        for everySeq in seqList:
            if self.verify('seqId', everySeq['sequence']):
                print 'INFO: seq already exists'
            else:
                self.insertData({"seqId":everySeq['sequence'],
                                "staff":everySeq['staffDep'],
                                "depot":everySeq['vehicleDep'],
                                "emuType":everySeq['emuType'].encode('utf8').encode('hex'),
                                "remark":everySeq['remark'].encode('utf8').encode('hex')})

        return 1

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
        
        if len(res):
            return 1, res
        else:
            return 0, []

    # def update(self, key, value):
    #     pass

def initalize():
    seqObj = table()
    seqObj.create()
    seqObj.importAll()

if __name__ == "__main__":
    initalize()

