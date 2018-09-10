#---#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('arrival', '../dbmaria/arrival.py')
loadModule('train', '../dbmaria/train.py')
loadModule('trainCode', '../dbmaria/trainCode.py')
loadModule('staInfo', '../dbmaria/staInfo.py')
loadModule('proxy', '../dbmaria/proxy.py')
loadModule('tool', '../tool/tool.py')

import arrival
import train
import trainCode
import staInfo
import proxy
import tool
import json

header ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
         "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}
arrUrl = 'http://mobile.12306.cn/weixin/czxx/queryByTrainNo?train_no={}&from_station_telecode=BBB&to_station_telecode=BBB&depart_date={}'
verify = 1

class trainArrHook(object):

    def __init__(self):
        self.arrivalDb = arrival.table()
        self.trainDb = train.table()
        self.codeDb = trainCode.table()
        self.stationDb = staInfo.table()
        self.proxyDb = proxy.table()

    def addTrain(self, trainStr, date):
        import json, time
        codeStatus, codeInfo = self.codeDb.search(trainStr, date)
        if codeStatus:
            arrData = json.loads(self.proxyGet(codeInfo[0]['trainCode'], codeInfo[0]['departDate']))
            if len(arrData):
                arrList = arrData['data']['data']
                finalList = []
                arrList[0]['arrive_time'] = '24:01'
                arrList[-1]['start_time'] = '24:01'
                for everyArrival in arrList:
                    stationStatus, stationInfo = self.stationDb.search('staCn', everyArrival['station_name'].encode('utf8').encode('hex'))
                    if stationStatus:
                        staTele = stationInfo[0]['staTele']
                    else:
                        specialStationCount = self.stationDb.verifySpecial(10001)
                        staTele = '{:0>3}'.format(specialStationCount+1)
                        self.stationDb.insert({'staCn':everyArrival['station_name'].encode('utf8').encode('hex'),
                                               'staTele':staTele,
                                               'staPy':'0000',
                                               'staNum':specialStationCount+10001})
                        print 'INSERT NEW STATION ' + everyArrival['station_name']
                    # print staTele

                    arrTime = tool.str2int(everyArrival['arrive_time'])
                    depTime = tool.str2int(everyArrival['start_time'])

                    finalList.append({"staTele":staTele,
                                    "staRank":int(everyArrival['station_no']),
                                    "trainStr":trainStr,
                                    "arrTime":arrTime,
                                    "depTime":depTime})
                
                del arrData, arrList

                arrDate = 0
                depDate = 1
                for arrivalNo in range(1, len(finalList)):
                    if finalList[arrivalNo]['arrTime'] < finalList[arrivalNo-1]['arrTime']:
                        arrDate = arrDate + 1
                    if finalList[arrivalNo]['depTime'] < finalList[arrivalNo-1]['depTime']:
                        depDate = depDate + 1
                    finalList[arrivalNo]['arrDate'] = arrDate
                    finalList[arrivalNo]['depDate'] = depDate
                finalList[0]['arrDate'] = 1
                finalList[0]['depDate'] = 1

                for everyArrival in finalList:
                    self.arrivalDb.insertDict(everyArrival)

                writeLog('SUCCESS : '+ trainStr)
                print 'INSERT SUCCESSFULLY'
                time.sleep(1)
            else:
                writeBC(trainStr)
                writeLog('TOO MANY BAD CONNECTIONS : '+ trainStr)
                print 'TOO MANY BAD CONNECTIONS WITH ' + trainStr

        else:
            print 'THIS TRAIN DO NOT OPERATE ON ' + date

        print '-'*36

    def proxyGet(self, trainCode, date):
        import urllib2
        res = '[]'
        fail = 0
        while (fail < 5):
            proxyCount, randomProxy = self.proxyDb.random('HTTP')
            proxyUrl = "http://user:password@"+randomProxy[0]['address']+':'+str(randomProxy[0]['port'])
            proxySupport = urllib2.ProxyHandler({'http':proxyUrl})
            opener = urllib2.build_opener(proxySupport)
            urllib2.install_opener(opener)
            request = urllib2.Request(arrUrl.format(trainCode, date), headers=header)
            try:
                if verify:
                    print urllib2.urlopen('http://icanhazip.com', timeout=4).read()[0:-1]
                res = urllib2.urlopen(request, timeout=5).read()
            except Exception as error:
                print 'ERROR OCCURS'
                print error
                fail = fail + 1
                randomProxy[0]['failTimes'] = randomProxy[0]['failTimes'] + 1
            finally:
                randomProxy[0]['connectTimes'] = randomProxy[0]['connectTimes'] + 1
                self.proxyDb.updateStatus(randomProxy[0]['proxyId'], randomProxy[0]['connectTimes'], randomProxy[0]['failTimes'])
                if res != '[]':
                    break

        return res

    def regionGet(self, start, end, trainClass):
        from datetime import date
        import time
        regionStatus, trainList = self.trainDb.searchList(start, end, trainClass)
        print '{} TRAIN(S) IN THIS REGION'.format(regionStatus)
        for everyTrain in trainList:
            print 'INSERT ' + everyTrain['trainStr']
            self.addTrain(everyTrain['trainStr'], date.today().strftime("%Y-%m-%d"))
            time.sleep(1)

    def getMissingTrain(self, vacancyTrainFile='vacancyList.json'):
        from datetime import date
        with open(vacancyTrainFile, 'r') as fi:
            vacancyList = json.load(fi)
        for everyTrain in vacancyList:
            self.addTrain(everyTrain, date.today().strftime("%Y-%m-%d"))
        

    def check(self, trainClass, start=0, end=10000):
        regionStatus, trainList = self.trainDb.searchList(start, end, trainClass)
        print 'WE NEED TO CHECK {} TRAIN(S)'.format(regionStatus)
        vacancyList = []
        for everyTrain in trainList:
            if not(self.arrivalDb.verifyArrival(everyTrain['trainStr'])):
                vacancyList.append(everyTrain['trainStr'])
                print 'ARRIVAL OF {} DO NOT EXIST'.format(everyTrain['trainStr'])
        
        with open('vacancyList.json', 'a+') as fo:
            json.dump(vacancyList, fo)


def writeLog(info, logFile='arrHookLog.txt'):
    import datetime
    with open(logFile, 'a+') as fo:
        fo.write(datetime.datetime.now().strftime('%Y%m%d%H%M%S') + ' - ' + info)

def writeBC(trainStr, bcFile='bcTrain.txt'):
    with open(bcFile, 'a+') as fo:
        fo.write(trainStr+',')


class run(object):
    
    def __init__(self):
        self.obj = trainArrHook()

    def add(self):
        startNum = raw_input('startNum:')
        endNum = raw_input('endNum:')
        trainClass = raw_input('trainClass:')
        self.obj.regionGet(int(startNum), int(endNum), trainClass)

    def check(self):
        startNum = raw_input('startNum:')
        endNum = raw_input('endNum:')
        trainClass = raw_input('trainClass:')
        self.obj.check(trainClass, int(startNum), int(endNum))
    
    def addMiss(self):
        self.obj.getMissingTrain()


if __name__ == "__main__":
    import sys
    myObj = run()
    if sys.argv[1] == 'add':
        myObj.add()
    elif sys.argv[1] == 'che':
        myObj.check()
    elif sys.argv[1] == 'ams':
        myObj.addMiss()
    else:
        print 'WHAT DO YOU WANT TO DO?'
