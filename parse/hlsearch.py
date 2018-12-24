#----------------------------------------------------------------#
# Module Name: hlsearch(high-level search) #
# Function: Connect the database and return info to the parse module. #
# Author: Kumo #
# Last Edit: Dec/24/2018 #
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
        print 'high level search loaded'

    def seqs(self, trainNum, trainClass):
        reply = trainClass + str(trainNum) + ' '
        trainDB = train.table()
        trainStatus, trainInfo = trainDB.searchDual(trainClass, str(trainNum))
        if not trainStatus:
            print chnword.trainDoNotExist.decode('hex')
            return reply + chnword.trainDoNotExist.decode('hex')
        arrivalTable = arrival.table()
        staTable = staInfo.table()
        arrStatus, arrInfo = arrivalTable.search(trainInfo[0]['trainStr'])
        firstStatus, firstInfo = staTable.search('staTele', arrInfo[0]['staTele'])
        lastStatus, lastInfo = staTable.search('staTele', arrInfo[-1]['staTele'])
        reply = reply + firstInfo[0]['staCn'].decode('hex') + '-' + lastInfo[0]['staCn'].decode('hex') + '\n'
        del arrStatus, firstStatus, lastStatus, arrInfo
        del arrivalTable, staTable
        seqDB = seq.table()
        depotDB = depot.table()
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

        print reply[0:-1]

        return reply[0:-1]
    
    def arrs(self, trainNum, trainClass):
        trainDB = train.table()
        trainStatus, trainInfo = trainDB.searchDual(trainClass, int(trainNum))
        if not trainStatus:
            print chnword.trainDoNotExist.decode('hex')
            return chnword.trainDoNotExist.decode('hex')
        reply = chnword.trainNo.decode('hex') + ':' + trainClass + str(trainNum) +'\n'
        arrivalDB = arrival.table()
        stationDB = staInfo.table()
        arrStatus, arrInfo = arrivalDB.search(trainInfo[0]['trainStr'])
        del arrStatus
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

        print reply[0:-1]

        return reply[0:-1]

    def dbs(self, staPy):
        stationDB = staInfo.table()
        stationStatus, stationInfo = stationDB.search('staPy', staPy.lower())
        if not stationStatus:
            print chnword.stationDoNotExist.decode('hex')
            return chnword.stationDoNotExist.decode('hex')
        reply = ''
        for everySta in stationInfo:
            reply = reply + chnword.station.decode('hex') + ':' + everySta['staTele'].encode('utf8') + ' '
            reply = reply + chnword.telecode.decode('hex') + ':' + everySta['staCn'].decode('hex') + '\n'

        print reply[0:-1]

        return reply[0:-1]

    def pss(self, EMUNo):
        print tool.processEmuno(str(EMUNo))
        return tool.processEmuno(str(EMUNo))

def test():
    trainNo = raw_input()
    hlsobj = hls()
    hlsobj.pss(int(trainNo))

if __name__ == "__main__":
    test()
