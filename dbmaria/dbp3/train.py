#----------------------------------------------------------------#
# Module Name: Train #
# Function: Define commands to control items in TRAIN table. #
# Author: Kumo #
# Last Edit: Dec/14/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', '../dbmaria2.py')

from dbmaria import dbBase
import json

webClass = ['G', 'D', 'C', 'Z', 'T', 'K', 'O']
actualClass = ['G', 'D', 'C', 'Z', 'T', 'K', 'S', 'Y', 'P']

class table(dbBase):

    def __init__(self):
        dbBase.__init__(self, 'train')

    def create(self, definitionFile='train_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

# ImportFile function is already moved to trainHook
#   def importFile(self, date, trainFile='trainData.json'):

    def insertBase(self, trainNum0, trainNum1, trainClass, trainStr, status):
        """Insert a train to the table.
           All parameters are required.
        """
        self.insertData({"trainNum0":trainNum0,
                         "trainNum1":trainNum1,
                         "trainClass":trainClass,
                         "trainStr":trainStr,
                         "status":status
                         })
    
    def insertDict(self, parameterDict):
        """Insert data to database directly, using data dict directly.
        """
        self.insertData(parameterDict)

    def updateBase(self, OriginalTrain, PresentTrain, trainClass):
        """Change the trainNum1 value of a train.
           All parameters are required.
           TrainNum1 value of the item that OriginalTrain maches will be updated to PresentTrain.
        """
        self.updateData({"trainNum1":PresentTrain}, 
                       [{"trainNum0":OriginalTrain,
                         "trainClass":trainClass}])

    def updateStatus(self, trainNum, trainClass, status):
        """Change the status of a train.
           All parameters are required.
        """
        self.updateData({"status":status},
                       [{"trainClass":trainClass},
                        {"trainNum0":trainNum,
                         "trainNum1":trainNum}],
                        OASequence=1)

    def updateSeq(self, trainStr, seqId, seqRank):
        """Change the seq value of a train.
           All parameters are required.
           SeqId is the serial number of the sequence they subordinated.
           SeqRank is the sort in this sequence.
        """
        self.updateData({"seqId":seqId,
                         "seqRank":seqRank},
                       [{"trainStr":trainStr}])

    def verifyTrain(self, trainClass, trainNum):
        """Count the trains that match the condition.
           The trainClass must be a charater and trainNum must be a integer less than 1w.
           A list of dict that contrains the result will be returned.
        """
        res = self.verifyExistence([{"trainClass":trainClass},
                                    {"trainNum0":trainNum,
                                     "trainNum1":trainNum}],
                                    OASequence=1)
        return res[0]['COUNT(1)']
    
    def verifyStr(self, trainStr):
        """Verify the existence of a train.
           You should provide the trainStr of this item.
        """
        res = self.verifyExistence([{"trainStr":trainStr}])
        return res[0]['COUNT(1)']

    def verifySingle(self, trainClass, trainNum0):
        """Verify the existence of a train, using only the trainNum0 value.
           Parameters are all required.
        """
        res = self.verifyExistence([{"trainClass":trainClass,
                                     "trainNum0":trainNum0}])
        return res[0]['COUNT(1)']

# Edited Dec/14/2018: Change Meaningless defalue value to NONE #
    def delete(self, key=None, value=None):
        """Delete a train.
           Parameters are not essential, causing all data deleted.
           If provided, only defigned item will be deleted.
        """
        if key is None:
            self.deleteData([])
        else:
            self.deleteData([{key:value}])

    def search(self, key=None, value=None):
        """Search for train(s).
           Parameters are not essential, and all trains will be returned.
           If provided, the item they marked will be returned.
        """
        if key is None:
            res = self.queryData([])
        else:
            res = self.queryData([{key:value}])
        
        return len(res), res

    def searchList(self, start, end, trainClass):
        """Search for trains with trainNum in a particular range.
           The start & end parameter must be integers mark the buttom and top of the range.
           The trainClass must be a charater.
           Only the list of trainStrs and amount will be returned.
        """
        res = self.queryData([{"trainNum0":{"judge":"between", "start":start, "end":end},
                               "trainClass":trainClass,
                               "status":True}],
                               ['trainStr'])

        return len(res), res

    def searchSingle(self, trainClass, trainNum, status=True):
        """Search for a train with particular trainNum0.
           The trainClass must be a charater and trainNum must be a integer.
           Amount of the train and list of results will be returned.
        """
        res = self.queryData([{"trainNum0":trainNum,
                               "trainClass":trainClass,
                               "status":status}])

        return len(res), res

    def searchDual(self, trainClass, trainNum, status=True):
        """Search for a train having trainNum0 or trainNum1 ???????
           The trainClass must be a charater and trainNum must be a integer.
           Amount of the train and list of results will be returned.
        """
        res = self.queryData([{"trainNum0":trainNum, "trainNum1":trainNum},
                              {"trainClass":trainClass},
                              {"status":status}],
                              OASequence=1)

        return len(res), res

def initalize():
    obj = table()
    obj.create()

if __name__ == "__main__":
    initalize()
