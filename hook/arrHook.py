#----------------------------------------------------------------#
# Module Name: ArrHook #
# Function: Import train arrival data form web page. #
# Author: Kumo Lam(github.com/Kumo-YZX) #
# Last Edit: Dec/31/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('arrival', '../dbmaria/dbp4/arrival.py')
loadModule('train', '../dbmaria/dbp3/train.py')
loadModule('trainCode', '../dbmaria/dbp3/trainCode.py')
loadModule('staInfo', '../dbmaria/dbp1/staInfo.py')
loadModule('proxy', '../dbmaria/dbproxy/proxy.py')
loadModule('tool', '../tool/tool.py')

import arrival, train, trainCode
import staInfo, proxy, tool
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
        print 'arrHook.py: Info: trainArrHook Init done.'

    def addTrain(self, trainStr, date):
        """Add all arrival data of a train.
           Parameter date should be in YYYY-MM-DD format.
        """
        import time
        # Verify the operation status of specified train.
        # In fact, any day in operation is ok to catch arrival data of this train(differernt trainStr marks differernt train).
        codeStatus, codeInfo = self.codeDb.search(trainStr, date)
        if codeStatus:
            # Get arrival data by proxyGet function.
            rawArrData = self.proxyGet(codeInfo[0]['trainCode'], codeInfo[0]['departDate'])
            if rawArrData is not None:
                arrData = json.loads(rawArrData)
                arrList = arrData['data']['data']
                finalList = []
                if len(arrList):
                    # Replace arrive time of depart station and depart time of terminal station with 2401.
                    arrList[0]['arrive_time'] = '24:01'
                    arrList[-1]['start_time'] = '24:01'
                    # Write every arrival to database.
                    for everyArrival in arrList:
                        stationStatus, stationInfo = self.stationDb.search('staCn', everyArrival['station_name'].encode('utf8').encode('hex'))
                        if stationStatus:
                            staTele = stationInfo[0]['staTele']
                        else:
                            # The arrive station haven't been recorded.
                            specialStationCount = self.stationDb.verifySpecial(10001)
                            staTele = '{:0>3}'.format(specialStationCount+1)
                            self.stationDb.insert({'staCn':everyArrival['station_name'].encode('utf8').encode('hex'),
                                                'staTele':staTele,
                                                'staPy':'0000',
                                                'staNum':specialStationCount+10001})
                            print 'INSERT NEW STATION ' + everyArrival['station_name']
                        # print staTele
                        # Trainsfer time into integer format.
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
                    # Calculate the date of every arrival.
                    for arrivalNo in range(1, len(finalList)):
                        if finalList[arrivalNo]['arrTime'] < finalList[arrivalNo-1]['arrTime']:
                            arrDate = arrDate + 1
                        if finalList[arrivalNo]['depTime'] < finalList[arrivalNo-1]['depTime']:
                            depDate = depDate + 1
                        finalList[arrivalNo]['arrDate'] = arrDate
                        finalList[arrivalNo]['depDate'] = depDate
                    finalList[0]['arrDate'] = 1
                    finalList[0]['depDate'] = 1

                    # Write them to database.
                    for everyArrival in finalList:
                        self.arrivalDb.insertDict(everyArrival)

                    writeLog('SUCCESS : '+ trainStr)
                    print 'arrHook.py: Info: Add arrival successfully.'
                else:
                    print 'arrHook.py: Info: This train exists, but do not have arrival data.'
                time.sleep(1)
            else:
                # Log failed trains.
                # But do not write to vancyFile. To check failed trains, please use CHECK function.
                writeBC(trainStr)
                writeLog('TOO MANY BAD CONNECTIONS : '+ trainStr)
                print 'arrHook.py: Warning: Too many bad connections with [{}].'.format(trainStr)

        else:
            print 'arrHook.py: Warning: This train does not operate on {}.'.format(date)

        print '-'*36

    def proxyGet(self, trainCode, date):
        """Get reply from specified URL using proxy.
           Parameter must be provided.
        """
        import urllib2
        res = None
        # Fail time count.
        fail = 0
        while (fail < 5):
            # Load a random proxy
            proxyCount, randomProxy = self.proxyDb.random('HTTP')
            del proxyCount
            proxyUrl = "http://user:password@"+randomProxy[0]['address']+':'+str(randomProxy[0]['port'])
            proxySupport = urllib2.ProxyHandler({'http':proxyUrl})
            opener = urllib2.build_opener(proxySupport)
            urllib2.install_opener(opener)
            # Format a request
            request = urllib2.Request(arrUrl.format(trainCode, date), headers=header)
            try:
                if verify:
                    print urllib2.urlopen('http://icanhazip.com', timeout=4).read()[0:-1]
                res = urllib2.urlopen(request, timeout=5).read()
            # Handle errors
            except Exception as error:
                print 'arrHook.py: Error: Request error occurs'
                print error
                fail = fail + 1
                randomProxy[0]['failTimes'] = randomProxy[0]['failTimes'] + 1
            # write feedback to proxy database.
            finally:
                randomProxy[0]['connectTimes'] = randomProxy[0]['connectTimes'] + 1
                self.proxyDb.updateStatus(randomProxy[0]['proxyId'],
                                          randomProxy[0]['connectTimes'],
                                          randomProxy[0]['failTimes'])
                if res is not None:
                    break
        return res

    def regionGet(self, start, end, trainClass):
        """Get all arrivals in provided region.
           Parameter start and end marks the base and top of region.
        """
        from datetime import date, timedelta
        import time
        dateTomorrow = date.today() + timedelta(days = 1)
        regionStatus, trainList = self.trainDb.searchList(start, end, trainClass)
        print 'arrHook.py: Info: There are {} trains in this region.'.format(regionStatus)
        for everyTrain in trainList:
            print 'arrHook.py: Info: We are now import {}.'.format(everyTrain['trainStr'])
            self.addTrain(everyTrain['trainStr'], dateTomorrow.strftime("%Y-%m-%d"))
            time.sleep(1)

    def getMissingTrain(self, vacancyTrainFile='vacancyList.json'):
        """Add arrivals of failed trains.
           Parameter file name are optional.
        """
        from datetime import date, timedelta
        import time
        dateTomorrow = date.today() + timedelta(days = 1)
        with open(vacancyTrainFile, 'r') as fi:
            vacancyList = json.load(fi)
        print 'arrHook.py: Info: There are {} trains in this region.'.format(len(vacancyList))
        for everyTrain in vacancyList:
            print 'arrHook.py: Info: We are now import [{}].'.format(everyTrain)
            self.addTrain(everyTrain, dateTomorrow.strftime("%Y-%m-%d"))
            time.sleep(1)


    def check(self, trainClass, start=0, end=10000):
        """Check the arrival-catching status of every train.
           If the train don't have any arrival, mark it as failed and register to file.
        """
        regionStatus, trainList = self.trainDb.searchList(start, end, trainClass)
        print 'arrHook.py: Info: We need to check {} trains.'.format(regionStatus)
        vacancyList = []
        for everyTrain in trainList:
            if not(self.arrivalDb.verifyArrival(everyTrain['trainStr'])):
                vacancyList.append(everyTrain['trainStr'])
                print 'arrHook.py: Info: Arrival of {} do not exist.'.format(everyTrain['trainStr'])
        
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
        """Add new arrivals in startNum(included) and endNum(included) region.
        """
        startNum = raw_input('startNum:')
        endNum = raw_input('endNum:')
        trainClass = raw_input('trainClass:')
        self.obj.regionGet(int(startNum), int(endNum), trainClass)

    def check(self):
        """Check arrivals.
        """
        startNum = raw_input('startNum:')
        endNum = raw_input('endNum:')
        trainClass = raw_input('trainClass:')
        self.obj.check(trainClass, int(startNum), int(endNum))
    
    def addMiss(self):
        self.obj.getMissingTrain()

# Run the script.
if __name__ == "__main__":
    import sys
    myObj = run()
    if sys.argv[1] == 'add':
        myObj.add()
    elif sys.argv[1] == 'che':
        myObj.check()
    elif sys.argv[1] == 'ams':
        myObj.addMiss()
