#----------------------------------------------------------------#
# Module Name: hlsearch(high-level search) #
# Function: Connect the database and return info to the parse module. #
# Author: Kumo Lam(github.com/Kumo-YZX) #
# Last Edit: Dec/31/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('arrival', '../dbmaria/dbp4/arrival.py')
loadModule('staInfo', '../dbmaria/dbp1/staInfo.py')
loadModule('trainCode', '../dbmaria/dbp3/trainCode.py')
loadModule('train', '../dbmaria/dbp3/train.py')
loadModule('seq', '../dbmaria/dbp2/seq.py')
loadModule('depot', '../dbmaria/dbp2/depot.py')
loadModule('tool', '../tool/tool.py')

import arrival, staInfo, trainCode, train, seq, depot
import tool
import chnword

class hls(object):

    def __init__(self):
        print 'hlsearch.py: Info: High level search loaded.'

    def seqs(self, trainNum, trainClass):
        """Provide the sequence and department & terminal station of a train.
           Parameter trainNum and trainClass must be provided.
           Return value(Reply) is in Chn format.
        """
        reply = trainClass + str(trainNum) + ' '
        # Initialize the train/arrival/station table object.
        trainDB = train.table()
        arrivalTable = arrival.table()
        staTable = staInfo.table()
        # Search for the train.
        trainStatus, trainInfo = trainDB.searchDual(trainClass, str(trainNum))
        if not trainStatus:
            print 'hlseach.py: Warning: This train does not exist.'
            return reply + chnword.trainDoNotExist.decode('hex')
        arrStatus, arrInfo = arrivalTable.search(trainInfo[0]['trainStr'])
        # Search for the dep & arr station of this train.
        firstStatus, firstInfo = staTable.search('staTele', arrInfo[0]['staTele'])
        lastStatus, lastInfo = staTable.search('staTele', arrInfo[-1]['staTele'])
        reply = reply + firstInfo[0]['staCn'].decode('hex') + '-' + lastInfo[0]['staCn'].decode('hex') + '\n'
        del arrStatus, firstStatus, lastStatus, arrInfo
        del arrivalTable, staTable
        # Initialize the sequence/depot table object.
        seqDB = seq.table()
        depotDB = depot.table()
        # Search for the depot & sequence data.
        seqStatus, seqInfo = seqDB.search('seqID', trainInfo[0]['seqId'])
        reply = reply + chnword.EMUType.decode('hex') + ':' + seqInfo[0]['emuType'].decode('hex') + '\n'
        sDepotStatus, sDepotInfo = depotDB.search(int(seqInfo[0]['staff']))
        vDepotStatus, vDepotInfo = depotDB.search(int(seqInfo[0]['depot']))
        reply = reply + sDepotInfo[0]['depotCn'].decode('hex') + chnword.staffDep.decode('hex') + ' '
        reply = reply + vDepotInfo[0]['depotCn'].decode('hex') + chnword.vehicleDep.decode('hex') + '\n'
        del sDepotStatus, sDepotInfo, vDepotStatus, vDepotInfo
        seqTrainStatus, seqTrains = trainDB.search('seqId', trainInfo[0]['seqId'])
        del seqTrainStatus, seqStatus
        from operator import itemgetter
        reply = reply + chnword.seqNo.decode('hex') +':'
        # Sort the trains in the same sequence and format the reply.
        seqTrains = sorted(seqTrains, key=itemgetter('seqRank'))
        for everyTrain in seqTrains:
            reply = reply + tool.correctClass(everyTrain['trainClass']).encode('utf8')
            reply = reply + str(everyTrain['trainNum0'])
            if everyTrain['trainNum0'] != everyTrain['trainNum1']:
                tnStr0 = str(everyTrain['trainNum0'])
                tnStr1 = str(everyTrain['trainNum1'])
                reply = reply + '/'
                if len(tnStr0) == len(tnStr1):
                    for loca in range(len(tnStr0)):
                        if tnStr1[loca] != tnStr0[loca]:
                            reply = reply + tnStr1[loca]
                else:
                    reply = reply + tnStr1
            reply = reply + '-'

        return reply[0:-1]

    def arrs(self, trainNum, trainClass):
        """Get all the arrivals of a train.
           Parameter trainNum and trainClass must be provided.
           Return value(Reply) is in Chn format.
        """
        # Initialize the train/arrival/station table object.
        trainDB = train.table()
        arrivalDB = arrival.table()
        stationDB = staInfo.table()
        # Search for train data.
        trainStatus, trainInfo = trainDB.searchDual(trainClass, int(trainNum))
        if not trainStatus:
            print 'hlseach.py: Warning: This train does not exist.'
            return chnword.trainDoNotExist.decode('hex')
        reply = chnword.trainNo.decode('hex') + ':' + trainClass + str(trainNum) +'\n'
        # Search for all the arrivals.
        arrStatus, arrInfo = arrivalDB.search(trainInfo[0]['trainStr'])
        del arrStatus
        # Format them.
        for everyArr in arrInfo:
            stationStatus, stationInfo = stationDB.search('staTele', everyArr['staTele'])
            reply = reply + stationInfo[0]['staCn'].decode('hex') + (8-len(stationInfo[0]['staCn'])/3)*' '
            if everyArr['arrTime'] == 1441:
                reply = reply + '-----' + ' '
            else:
                reply = reply + tool.int2str(everyArr['arrTime']) + ' '

            if everyArr['depTime'] == 1441:
                reply = reply + '-----' + '\n'
            else:
                reply = reply + tool.int2str(everyArr['depTime']) + '\n'
        del stationStatus

        return reply[0:-1]

    def dbs(self, staPy):
        """Search for the telecode of a station.
           Parameter staPy is the first character of the station's pinyin.
        """
        stationDB = staInfo.table()
        stationStatus, stationInfo = stationDB.search('staPy', staPy.lower())
        if not stationStatus:
            print 'hlseach.py: Warning: This station does not exist.'
            return chnword.stationDoNotExist.decode('hex')
        reply = ''
        for everySta in stationInfo:
            reply = reply + chnword.station.decode('hex') + ':' + everySta['staTele'].encode('utf8') + ' '
            reply = reply + chnword.telecode.decode('hex') + ':' + everySta['staCn'].decode('hex') + '\n'

        return reply[0:-1]

    def pss(self, EMUNo):
        """Search for the infomation of a EMU train.
           Not avilable yet now.
        """
        print tool.processEmuno(str(EMUNo))
        return tool.processEmuno(str(EMUNo))

def test():
    import sys
    testObj = hls()
    if sys.argv > 1:
        actionName = sys.argv[1]
        actionParameter = sys.argv[2]
        if actionName == 'seq' or actionName == 's':
            # No need to transfer trainNum into integer format.
            print testObj.seqs(actionParameter[1:], actionParameter[0])
        elif actionName == 'arr' or actionName == 'a':
            print testObj.arrs(actionParameter[1:], actionParameter[0])
        elif actionName == 'dbs' or actionName == 'd':
            print testObj.dbs(actionParameter)
        else:
            print 'hlsearch.py: Info: Test ended because of wrong parameter.'
    else:
        print 'hlsearch.py: Info: Test ended with nothing happened.'

if __name__ == "__main__":
    test()
