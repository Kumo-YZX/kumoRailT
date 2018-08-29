#--#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', 'dbmaria.py')

from dbmaria import dbBase
import json

webClass = ['G', 'D', 'C', 'Z', 'T', 'K', 'O']
actualClass = ['G', 'D', 'C', 'Z', 'T', 'K', 'S', 'Y', 'P']

class table(dbBase):

    def __init__(self, configFile = 'dbconfig.json'):
        dbBase.__init__(self, 'train', configFile)

    def create(self, definitionFile='train_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def importFile(self, date, trainFile='trainData.json'):
        with open(trainFile) as fi:
            allDayList = json.load(fi)

        if date in allDayList:
            thisDayList = allDayList[date]
            del allDayList
            for trainClass in webClass:
                trainList = thisDayList[trainClass]
                trainListNo = 0
                while trainListNo < len(trainList):
                    trainNo = (trainList[trainListNo]['station_train_code'].split('('))[0]
                    trainList[trainListNo]['train_no'] = trainList[trainListNo]['train_no'][2:-2]
                    trainStr = ''
                    flag = 0
                    for everyChar in trainList[trainListNo]['train_no']:
                        if everyChar !='0':
                            flag = 1
                        if flag == 1:
                            trainStr = trainStr + everyChar

                    if trainNo[0] in actualClass:
                        trainNum = int(trainNo[1:])
                        trainClass = trainNo[0]
                        actualNum = int(trainStr[1:])
                    else:
                        trainNum = int(trainNo)
                        trainClass = 'A'
                        actualNum = int(trainStr)

                    if trainNo == trainStr:
                        self.insertData({"trainNum0":trainNum,
                                         "trainNum1":trainNum,
                                         "trainClass":trainClass,
                                         "trainVer":1
                        })
                    else:
                        diffNum = actualNum - trainNum
                    #    print 'diffNum' + str(diffNum)
                        if trainNum%2:
                            if diffNum == 3 or diffNum == 1:
                                self.insertData({"trainNum0":actualNum,
                                                 "trainNum1":trainNum,
                                                 "trainClass":trainClass,
                                                 "trainVer":1
                                })
                                del trainList[trainListNo+diffNum]
                            elif diffNum == -1:
                                self.updateData({"trainNum1":trainNum}, [{"trainNum0":{"judge":"=", "value":actualNum}}])

                            else:
                                print trainNo + '//' + trainStr
                                raise ValueError('Unprocessable trainNum')
                        else:
                            if diffNum == -3 or diffNum == -1:
                                self.updateData({"trainNum1":trainNum}, [{"trainNum0":{"judge":"=", "value":actualNum}}])
                            elif diffNum == 1:
                                self.insertData({"trainNum0":actualNum,
                                                 "trainNum1":trainNum,
                                                 "trainClass":trainClass,
                                                 "trainVer":1
                                })
                                del trainList[trainListNo+diffNum]
                            else:
                                print trainNo + '/-/' + trainStr
                                raise ValueError('Unprocessable trainNum')

                    trainListNo = trainListNo + 1

    def insertBase(self, trainNum0, trainNum1, trainClass, trainStr, status):
        self.insertData({"trainNum0":trainNum0,
                         "trainNum1":trainNum1,
                         "trainClass":trainClass,
                         "trainStr":trainStr,
                         "status":status
                         })

    def updateBase(self, OriginalTrain, PresentTrain, trainClass):
        self.updateData({"trainNum1":PresentTrain}, [{"trainNum0":{"judge":"=", "value":OriginalTrain}, "trainClass":{"judge":"=", "value":trainClass}}])

    def updateStatus(self, trainNum, trainClass, status):
        self.updateData({"status":status},
                        [{"trainClass":{"judge":"=", "value":trainClass},
                         "trainNum0":{"judge":"=", "value":trainNum}},
                         {"trainClass":{"judge":"=", "value":trainClass},
                         "trainNum1":{"judge":"=", "value":trainNum}}])

    def updateSeq(self, trainStr, seqId, seqRank):
        self.updateData({"seqId":seqId, "seqRank":seqRank},
                        [{"trainStr":{"judge":"=", "value":trainStr}}])

    def verifyTrain(self, trainClass, trainNum):
        res = self.verifyExistence([{"trainClass":{"judge":"=", "value":trainClass},
                                     "trainNum0":{"judge":"=", "value":trainNum}},
                                     {"trainClass":{"judge":"=", "value":trainClass},
                                     "trainNum1":{"judge":"=", "value":trainNum}}])
        return res
    
    def verifyStr(self, trainStr):
        res = self.verifyExistence([{"trainStr":{"judge":"=", "value":trainStr}}])
        return res

    def delete(self, key='', value=''):
        if key == '':
            self.deleteData()
        else:
            self.deleteData([{key:{"judge":"=", "value":value}}])

    def search(self, key='', value=''):
        if key == '':
            res = self.queryData()
        else:
            res = self.queryData([], [{key:{"judge":"=", "value":value}}])
        
        if len(res):
            return 1, res
        else:
            return 0, []

    def searchSingle(self, trainClass, trainNum, status=True):
        res = self.queryData([], [{"trainNum0":{"judge":"=", "value":trainNum},
                                  "trainClass":{"judge":"=", "value":trainClass},
                                  "status":{"judge":"=", "value":status}}])

        if len(res):
            return 1, res
        else:
            return 0, []

    def searchDual(self, trainClass, trainNum, status=True):
        res = self.queryData([], [{"trainNum0":{"judge":"=", "value":trainNum},
                                  "trainClass":{"judge":"=", "value":trainClass},
                                  "status":{"judge":"=", "value":status}},
                                  {"trainNum1":{"judge":"=", "value":trainNum},
                                  "trainClass":{"judge":"=", "value":trainClass},
                                  "status":{"judge":"=", "value":status}}
                                  ])

        if len(res):
            return 1, res
        else:
            return 0, []

def initalize():
    obj = table()
    obj.create()

if __name__ == "__main__":
    initalize()
