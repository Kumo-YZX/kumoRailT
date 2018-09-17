#migrate.py Export data to json files#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('arrival', '../dbmaria/arrival.py')
loadModule('train', '../dbmaria/train.py')
loadModule('trainCode', '../dbmaria/trainCode.py')
loadModule('proxy', '../dbmaria/proxy.py')
loadModule('tool', '../tool/tool.py')
loadModule('seq', '../dbmaria/seq.py')
loadModule('depot', '../dbmaria/depot.py')
loadModule('staInfo', '../dbmaria/staInfo.py')

import arrival
import train
import trainCode
import proxy
import tool
import seq
import depot
import staInfo
import json

class migrate(object):

    def __init__(self):
        self.arrival = arrival.table()
        self.train = train.table()
        self.trainCode = trainCode.table()
        self.proxy = proxy.table()
        self.seq = seq.table()
        self.depot = depot.table()
        self.staInfo = staInfo.table()

    def exportArrival(self, expFile='arrivalData/arrival_data_{}.json'):
        lastStatus, lastArrival = self.arrival.searchLast()
        arrivalList = []
        listAmount = 1
        for arrivalId in range(lastArrival[0]['arrivalId']+1):
            idStatus, idData = self.arrival.searchById(arrivalId)
            if idStatus:
                arrivalList.append(idData[0])
            if len(arrivalList) == 1000 or arrivalId == (lastArrival[0]['arrivalId']):
                with open(expFile.format(listAmount), 'w+') as fo:
                    json.dump(arrivalList, fo)
                print 'DEAL WITH LIST NO.{}'.format(listAmount)
                arrivalList = []
                listAmount = listAmount + 1

    def exportTrain(self, expFile='trainData/train_data_{}.json'):
        trainAmount, allTrain = self.train.search()
        trainList = []
        listAmount = 1
        for everyTrainIndex in range(trainAmount):
            trainList.append(allTrain[everyTrainIndex])
            if len(trainList) == 1000 or everyTrainIndex == (trainAmount-1):
                with open(expFile.format(listAmount), 'w+') as fo:
                    json.dump(trainList, fo)
                print 'DEAL WITH LIST NO.{}'.format(listAmount)
                trainList = []
                listAmount = listAmount + 1

    def exportTrainCode(self, expFile='trainCodeData/trainCode_data_{}.json'):

        codeAmount, allCode = self.trainCode.searchAll()
        codeList = []
        listAmount = 1
        for codeIndex in range(codeAmount):
            dateStr = allCode[codeIndex]['departDate'].strftime('%Y-%m-%d')
            del allCode[codeIndex]['departDate']
            allCode[codeIndex]['departDate'] = dateStr
            codeList.append(allCode[codeIndex])
            if len(codeList) == 1000 or codeIndex == (codeAmount-1):
                with open(expFile.format(listAmount), 'w+') as fo:
                    json.dump(codeList, fo)
                print 'DEAL WITH LIST NO.{}'.format(listAmount)
                codeList = []
                listAmount = listAmount + 1

    def exportSeq(self, expFile='seqData/seq_data_{}.json'):
        seqAmount, allSeq = self.seq.search()
        seqList = []
        listAmount = 1
        for seqIndex in range(seqAmount):
            seqList.append(allSeq[seqIndex])
            if len(seqList) == 1000 or seqIndex == (seqAmount-1):
                with open(expFile.format(listAmount), 'w+') as fo:
                    json.dump(seqList, fo)
                print 'DEAL WITH LIST NO.{}'.format(listAmount)
                seqList = []
                listAmount = listAmount + 1

    def exportStaInfo(self, expFile='staInfoData/staInfo_data_{}.json'):
        infoAmount, allInfo = self.staInfo.search()
        infoList = []
        listAmount = 1
        for infoIndex in range(infoAmount):
            infoList.append(allInfo[infoIndex])
            if len(infoList) == 1000 or infoIndex == (infoAmount-1):
                with open(expFile.format(listAmount), 'w+') as fo:
                    json.dump(infoList, fo)
                print 'DEAL WITH LIST NO.{}'.format(listAmount)
                infoList = []
                listAmount = listAmount + 1

    def exportDepot(self, expFile='depotData/depot_data_{}.json'):
        depotAmount, allDepot = self.depot.search()
        depotList = []
        listAmount = 1
        for depotIndex in range(depotAmount):
            depotList.append(allDepot[depotIndex])
            if len(depotList) == 1000 or depotIndex == (depotAmount-1):
                with open(expFile.format(listAmount), 'w+') as fo:
                    json.dump(depotList, fo)
                print 'DEAL WITH LIST NO.{}'.format(listAmount)
                depotList = []
                listAmount = listAmount + 1

    def exportProxy(self, expFile='proxyData/proxy_data_{}.json'):
        proxyAmount, allProxy = self.proxy.search()
        proxyList = []
        listAmount = 1
        for proxyIndex in range(proxyAmount):
            proxyList.append(allProxy[proxyIndex])
            if len(proxyList) == 1000 or proxyIndex == (proxyAmount-1):
                with open(expFile.format(listAmount), 'w+') as fo:
                    json.dump(proxyList, fo)
                print 'DEAL WITH LIST NO.{}'.format(listAmount)
                proxyList = []
                listAmount = listAmount + 1

    def importSeq(self, impFile='seqData/seq_data_{}.json', fileAmount=4):
        for everyFile in range(1,fileAmount):
            with open(impFile.format(everyFile), 'r') as fi:
                dataList = json.load(fi)

            for every in dataList:
                self.seq.insert(every)

    def importStaInfo(self, impFile='staInfoData/staInfo_data_{}.json', fileAmount=4):
        for everyFile in range(1,fileAmount):
            with open(impFile.format(everyFile), 'r') as fi:
                dataList = json.load(fi)

            for every in dataList:
                self.staInfo.insert(every)

    def importTrain(self, impFile='trainData/train_data_{}.json', fileAmount=4):
        for everyFile in range(1,fileAmount):
            with open(impFile.format(everyFile), 'r') as fi:
                dataList = json.load(fi)

            for every in dataList:
                self.train.insertDict(every)

    def importTrainCode(self, impFile='trainCodeData/trainCode_data_{}.json', fileAmount=4):
        for everyFile in range(1,fileAmount):
            with open(impFile.format(everyFile), 'r') as fi:
                dataList = json.load(fi)

            for every in dataList:
                self.trainCode.insertDict(every)

    def importArrival(self, impFile='arrivalData/arrival_data_{}.json', fileAmount=4):
        for everyFile in range(1,fileAmount):
            with open(impFile.format(everyFile), 'r') as fi:
                dataList = json.load(fi)

            for every in dataList:
                self.arrival.insertDict(every)

    def importDepot(self, impFile='depotData/depot_data_{}.json', fileAmount=4):
        for everyFile in range(1,fileAmount):
            with open(impFile.format(everyFile), 'r') as fi:
                dataList = json.load(fi)

            for every in dataList:
                self.depot.insertDict(every)

    def importProxy(self, impFile='proxyData/proxy_data_{}.json', fileAmount=4):
        for everyFile in range(1,fileAmount):
            with open(impFile.format(everyFile), 'r') as fi:
                dataList = json.load(fi)

            for every in dataList:
                self.proxy.insertDict(every)

if __name__ == '__main__':
    import sys
    obj = migrate()
    if sys.argv[1] == 'exp':
        if sys.argv[2] == 'train':
            obj.exportTrain()
        elif sys.argv[2] == 'arrival':
            obj.exportArrival()
        elif sys.argv[2] == 'trainCode':
            obj.exportTrainCode()
        elif sys.argv[2] == 'seq':
            obj.exportSeq()
        elif sys.argv[2] == 'staInfo':
            obj.exportStaInfo()
        elif sys.argv[2] == 'depot':
            obj.exportDepot()
        elif sys.argv[2] == 'proxy':
            obj.exportProxy()
        else:
            print 'WHAT DO YOU WANT TO DO'
    elif sys.argv[1] == 'imp':
        if sys.argv[2] == 'train':
            obj.importTrain()
        elif sys.argv[2] == 'arrival':
            obj.importArrival()
        elif sys.argv[2] == 'trainCode':
            obj.importTrainCode()
        elif sys.argv[2] == 'seq':
            obj.importSeq()
        elif sys.argv[2] == 'staInfo':
            obj.importStaInfo()
        elif sys.argv[2] == 'depot':
            obj.importDepot()
        elif sys.argv[2] == 'proxy':
            obj.importProxy()
        else:
            print 'WHAT DO YOU WANT TO DO'
    else:
        print 'WHAT DO YOU WANT TO DO'







