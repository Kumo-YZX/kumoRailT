#---#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('train', '../dbmaria/train.py')
loadModule('trainCode', '../dbmaria/trainCode.py')

import train 
import trainCode
import json

webClass = ['G', 'D', 'C', 'Z', 'T', 'K', 'O']
actualClass = ['G', 'D', 'C', 'Z', 'T', 'K', 'S', 'Y', 'P']
trainVer = 1

class trainInfoHook(object):

    def __init__(self):
        self.trainDb = train.table()
        self.codeDb = trainCode.table()

    def importFile(self, trainFile='trainData.json'):
        with open(trainFile) as fi:
            self.allList = json.load(fi)

    def importWeb(self, site=''):
        import urllib2
        self.allList = json.loads(urllib2.urlopen(site, timeout=12).read())

    def writeTrain(self, date):
        allDayList = self.allList

        if date in allDayList:
            thisDayList = allDayList[date]
            del allDayList
            for trainClass in webClass:
                trainList = thisDayList[trainClass]
                trainListNo = 0
                while trainListNo < len(trainList):
                    trainNo = (trainList[trainListNo]['station_train_code'].split('('))[0]
                    trainStr = ''
                    flag = 0
                    for everyChar in trainList[trainListNo]['train_no'][2:-2]:
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

                    InternalStr = '{:0>8}'.format(str(trainVer) + trainClass + str(actualNum))
                    if self.trainDb.verifyTrain(trainClass, trainNum):
                        self.codeDb.insert(InternalStr, date, trainList[trainListNo]['train_no'])
                        # print 'TrainStr:{}, date:{}, trainCode:{}'.format(InternalStr, date, trainList[trainListNo]['train_no'])
                    else:
                        if trainNo == trainStr:
                            self.trainDb.insertBase(trainNum, trainNum, trainClass, InternalStr)
                            self.codeDb.insert(InternalStr, date, trainList[trainListNo]['train_no'])
                        else:
                            diffNum = actualNum - trainNum
                        #    print 'diffNum' + str(diffNum)
                            if trainNum%2:
                                if diffNum == 3 or diffNum == 1:
                                    self.trainDb.insertBase(actualNum, trainNum, trainClass, InternalStr)
                                    self.codeDb.insert(InternalStr, date, trainList[trainListNo]['train_no'])
                                    del trainList[trainListNo+diffNum]
                                elif diffNum == -1:
                                    self.trainDb.updateBase(actualNum, trainNum, trainClass)

                                else:
                                    print trainNo + '//' + trainStr
                                    print 'Unprocessable trainNum'
                            else:
                                if diffNum == -3 or diffNum == -1:
                                    self.trainDb.updateBase(actualNum, trainNum, trainClass)
                                elif diffNum == 1:
                                    self.trainDb.insertBase(actualNum, trainNum, trainClass, InternalStr)
                                    self.codeDb.insert(InternalStr, date, trainList[trainListNo]['train_no'])
                                    del trainList[trainListNo+diffNum]
                                else:
                                    print trainNo + '/-/' + trainStr
                                    print 'Unprocessable trainNum'

                    trainListNo = trainListNo + 1

    def writeTrain2(self, date):
        
        if date in self.allList:
            for everyClass in webClass:
                trainList = self.allList[date][everyClass]
                for everyTrain in trainList:
                    trainNo = (everyTrain['station_train_code'].split('('))[0]
                    trainStr = ''
                    flag = 0
                    for everyChar in everyTrain['train_no'][2:-2]:
                        if everyChar != '0':
                            flag = 1
                        if flag == 1:
                            trainStr = trainStr + everyChar

                    if trainNo[0] in actualClass:
                        trainNum = int(trainNo[1:])
                        actualNum = int(trainStr[1:])
                        trainClass = trainNo[0]
                    else:
                        trainNum = int(trainNo)
                        actualNum = int(trainStr)
                        trainClass = 'A'

                    internalStr = '{:0>8}'.format(str(trainVer) + trainClass + str(actualNum))
                    if not(self.trainDb.verifyStr(internalStr)):
                        self.trainDb.updateStatus(trainNum, trainClass, False)
                        self.trainDb.insertBase(actualNum, trainNum, trainClass, internalStr, True)
                    
                    if trainNo == trainStr:
                        self.codeDb.insert(internalStr, date, everyTrain["train_no"])

                for everyTrain in trainList:
                    trainNo = (everyTrain['station_train_code'].split('('))[0]
                    trainStr = ''
                    flag = 0
                    for everyChar in everyTrain['train_no'][2:-2]:
                        if everyChar != '0':
                            flag = 1
                        if flag == 1:
                            trainStr = trainStr + everyChar

                    if trainNo[0] in actualClass:
                        trainNum = int(trainNo[1:])
                        actualNum = int(trainStr[1:])
                        trainClass = trainNo[0]
                    else:
                        trainNum = int(trainNo)
                        actualNum = int(trainStr)
                        trainClass = 'A'

                    internalStr = '{:0>8}'.format(str(trainVer) + trainClass + str(actualNum))
                    if trainNo != trainStr:
                        self.trainDb.updateBase(actualNum, trainNum, trainClass)

    def writeCode(self, date):

        if date in self.allList:
            for everyClass in webClass:
                trainList = self.allList[date][everyClass]
                for everyTrain in trainList:
                    trainNo = (everyTrain['station_train_code'].split('('))[0]

                    if trainNo[0] in actualClass:
                        trainNum = int(trainNo[1:])
                        trainClass = trainNo[0]
                    else:
                        trainNum = int(trainNo)
                        trainClass = 'A'

                    trainStatus, trainInfo = self.trainDb.searchDual(trainClass, trainNum)
                    if trainStatus:
                        self.codeDb.insert(trainInfo[0]["trainStr"], date, everyTrain["train_no"])
                    else:
                        print everyTrain['station_train_code'] + ' NOT EXIST'



class test(object):
    
    def __init__(self):
        self.myhook = trainInfoHook()

    def get(self):
        from datetime import date, timedelta
        self.myhook.importFile()
        myDate = date.today()

        for dayDelta in range(10):
            myDate = myDate + timedelta(days=1)
            myDateStr = myDate.strftime("%Y-%m-%d")
            if myDateStr in self.myhook.allList:
                self.myhook.writeTrain2(myDateStr)
                print 'WRITE ' + myDateStr
            else:
                print 'END AT ' + myDateStr
                break

if __name__ == "__main__":
    obj = test()
    obj.get()