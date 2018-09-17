#-----#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('seq', '../dbmaria/seq.py')
loadModule('train', '../dbmaria/train.py')

import seq
import train

class seqHook(object):

    def __init__(self):
        self.seqDb = seq.table()
        self.trainDb = train.table()

    def process(self, start, end, fileName='seq.json'):
        specialTrainList = ['0G', '0D', 'DJ', '0C']
        import json
        with open(fileName, 'r') as fi:
            seqList = json.load(fi)
        seqList = seqList[1:]
        for everySeq in seqList:
            if everySeq['seqNum'] >= start and everySeq['seqNum'] < end:
                print 'DEAL WITH {}'.format(everySeq['seqNum'])
                seqRank = 0
                for everyTrain in everySeq['seqTrains']:
                    version = 1
                    if everyTrain[0:2] == specialTrainList[0]:
                        if len(everyTrain) == 2:
                            version = version + self.trainDb.verifySingle('h', 0)
                            trainStr = '{:0>8}'.format(str(version) + 'h')
                            self.trainDb.insertBase(0, 0, 'h', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                        else:
                            trainNum = int(everyTrain[2:])
                            version = version + self.trainDb.verifySingle('h', trainNum)
                            trainStr = '{:0>8}'.format(str(version) + 'h' + str(trainNum))
                            self.trainDb.insertBase(trainNum, trainNum, 'h', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                    elif everyTrain[0:2] == specialTrainList[1]:
                        if len(everyTrain) == 2:
                            version = version + self.trainDb.verifySingle('e', 0)
                            trainStr = '{:0>8}'.format(str(version) + 'e')
                            self.trainDb.insertBase(0, 0, 'e', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                        else:
                            trainNum = int(everyTrain[2:])
                            version = version + self.trainDb.verifySingle('e', trainNum)
                            trainStr = '{:0>8}'.format(str(version) + 'e' + str(trainNum))
                            self.trainDb.insertBase(trainNum, trainNum, 'e', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                    elif everyTrain[0:2] == specialTrainList[2]:
                        if len(everyTrain) == 2:
                            version = version + self.trainDb.verifySingle('j', 0)
                            trainStr = '{:0>8}'.format(str(version) + 'j')
                            self.trainDb.insertBase(0, 0, 'j', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                        else:
                            trainNum = int(everyTrain[2:])
                            version = version + self.trainDb.verifySingle('j', trainNum)
                            trainStr = '{:0>8}'.format(str(version) + 'j' + str(trainNum))
                            self.trainDb.insertBase(trainNum, trainNum, 'j', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                    elif everyTrain[0:2] == specialTrainList[3]:
                        if len(everyTrain) == 2:
                            version = version + self.trainDb.verifySingle('b', 0)
                            trainStr = '{:0>8}'.format(str(version) + 'b')
                            self.trainDb.insertBase(0, 0, 'b', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                        else:
                            trainNum = int(everyTrain[2:])
                            version = version + self.trainDb.verifySingle('b', trainNum)
                            trainStr = '{:0>8}'.format(str(version) + 'b' + str(trainNum))
                            self.trainDb.insertBase(trainNum, trainNum, 'b', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                    else:
                        trainStatus, trainInfo = self.trainDb.searchSingle(everyTrain[0], int(everyTrain[1:]))
                        if trainStatus:
                            self.trainDb.updateSeq(trainInfo[0]['trainStr'], everySeq['seqNum'], seqRank)
                    seqRank = seqRank + 1


def test():
    obj = seqHook()
    start = raw_input('start:')
    end = raw_input('end:')
    obj.process(int(start), int(end))

if __name__ == "__main__":
    test()




