#----------------------------------------------------------------#
# Module Name: SeqHook(SequenceHook) #
# Function: Import the sequence number and rank of every train from local file. #
# Author: Kumo Lam(github.com/Kumo-YZX) #
# Last Edit: Dec/31/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('seq', '../dbmaria/dbp2/seq.py')
loadModule('train', '../dbmaria/dbp3/train.py')

import seq
import train

class seqHook(object):

    def __init__(self):
        self.seqDb = seq.table()
        self.trainDb = train.table()

    def process(self, start, end, fileName='seq.json'):
        """Import seq data from file.
           Parameter start and end mark the region of seq.
        """
        # List of class of cheching trains.
        # Checking trains do not exist in raw train tables.
        specialTrainList = ['0G', '0D', 'DJ', '0C']
        import json
        with open(fileName, 'r') as fi:
            seqList = json.load(fi)
        # Remove seq0, which records all the trains that do not have a sequence.
        seqList = seqList[1:]
        for everySeq in seqList:
            if everySeq['seqNum'] >= start and everySeq['seqNum'] < end:
                print 'seqHook.py: Info: Dealing with sequence No.[{}]'.format(everySeq['seqNum'])
                # The rank in this sequence.
                seqRank = 0
                # Add every train.
                for everyTrain in everySeq['seqTrains']:
                    version = 1
                    # Deal with 0G class checking trains.
                    if everyTrain[0:2] == specialTrainList[0]:
                        # The trainNum does not have a number. The same as following conditions.
                        if len(everyTrain) == 2:
                            # The recorded class of OG is 'h'.
                            # Get the amount of existing same-class checking trains and format the new version.
                            version = version + self.trainDb.verifySingle('h', 0)
                            # Format the trainStr.
                            trainStr = '{:0>8}'.format(str(version) + 'h')
                            # Write train information and sequence to database.
                            self.trainDb.insertBase(0, 0, 'h', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                        # Normal conditions.
                        else:
                            # Get the number. The same as following conditons.
                            trainNum = int(everyTrain[2:])
                            # Get the amount of existing same-class checking trains and format the new version.
                            # Remand: Checking trains with number can also be repeated.
                            version = version + self.trainDb.verifySingle('h', trainNum)
                            trainStr = '{:0>8}'.format(str(version) + 'h' + str(trainNum))
                            self.trainDb.insertBase(trainNum, trainNum, 'h', trainStr, 0)
                            self.trainDb.updateSeq(trainStr, everySeq['seqNum'], seqRank)
                    # Deal with 0D class checking trains.
                    elif everyTrain[0:2] == specialTrainList[1]:
                        if len(everyTrain) == 2:
                            # The recorded class of 0D is 'e'.
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
                    # Deal with DJ class checking trains.
                    elif everyTrain[0:2] == specialTrainList[2]:
                        if len(everyTrain) == 2:
                            # The recorded class of DJ is 'j'.
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
                    # Deal with 0C class checking trains.
                    elif everyTrain[0:2] == specialTrainList[3]:
                        if len(everyTrain) == 2:
                            # The recorded class of 0C is 'b'.
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
                    # Deal with normal trains.
                    # Remind: A train in seq.json but not in database, the data will be ignored.
                    # Remind: A train in database but not in seq.json, their seqId & seqRank will be NULL.
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