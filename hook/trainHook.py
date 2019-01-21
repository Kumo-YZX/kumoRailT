#----------------------------------------------------------------#
# Module Name: TrainHook #
# Funtion: Import train&trainCode data from local file. #
# Author: Kumo Lam(github.com/Kumo-YZX) #
# Last Edit: Dec/28/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('train', '../dbmaria/dbp3/train.py')
loadModule('trainCode', '../dbmaria/dbp3/trainCode.py')
loadModule('proxy', '../dbmaria/dbproxy/proxy.py')

import train 
import trainCode
import proxy
import json, time

normalClass = ['G', 'D', 'C', 'Z', 'T', 'K']
specialClass = ['Y', 'P', 'S']
ipVerify = 1
trainVer = 1
header ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
         "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}

class trainWebHook(object):

    def __init__(self):
        self.apiAddress='https://search.12306.cn/search/v1/train/search?keyword={}&date={}'
        self.proxyDb = proxy.table()
        self.trainDb = train.table()
        self.codeDb = trainCode.table()
        print 'trainHook.py: Info: trainWebHook Init done'

    def catchNormal(self, dateStr):
        """Catch all trainNums in normal class.
           Parameter dateStr must be in YYYYMMDD format.
        """
        for everyClass in normalClass:
            self.thisClassFailList = []
            # Verify numbers less than 1000
            for singleBit in range(1,10):
                # Send request and get reply using proxy
                self.reqRep(everyClass + str(singleBit), dateStr, 1)
                print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(everyClass + str(singleBit))
                time.sleep(4)
            print 'trainHook.py: Info: Verify trainNums that less than 1k ends.'
            # Verify numbers more than 1000
            for multiBit in range(10, 100):
                # Send request and get reply using proxy.
                self.reqRep(everyClass + str(multiBit), dateStr)
                print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(everyClass + str(multiBit))
                time.sleep(4)
            self.logFailTrain()
            print 'trainHook.py: Info: Verify trainNums that more than 1k ends.'

    def catchLocal(self, dateStr):
        """Catch all trainNums in local class.
           Local trains have their trainNum in 4-bits number only.
        """
        self.thisClassFailList = []
        # Use a 2-bit number as keyword.
        for multiBit in range(10, 100):
            self.reqRep(str(multiBit), dateStr, 2)
            print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(str(multiBit))
            time.sleep(4)
        self.logFailTrain()
        print 'trainHook.py: Info: Verify local trains ends.'

    def catchTravel(self, dateStr):
        """Catch all trainNums of travel trains.
           Travel trains have their trainNums in Pxxx format.
        """
        self.thisClassFailList = []
        # Use Y1-Y9 as keywords.
        trainClass = 'Y'
        for singleBit in range(1,10):
            self.reqRep(trainClass + str(singleBit), dateStr, 1)
            print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(trainClass + str(singleBit))
            time.sleep(4)
        self.logFailTrain()
        print 'trainHook.py: Info: Verify travel trains ends.'

    def catchCrossborder(self, dateStr):
        """Catch all trainNums of Crossborder trains(Kowloon-Shanghai/Beijing Through Train)
           TrainNums contains P97-P100 only, So I use P as keyword directly.
        """
        self.thisClassFailList = []
        trainClass = 'P'
        self.reqRep(trainClass, dateStr, 1)
        print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(trainClass)
        self.logFailTrain()
        print 'trainHook.py: Info: Verify crossborder trains ends.'

    def reqRep(self, trainKeyWord, dateStr, judgement=0):
        """Send request and get reply from API.
           Divided from catchNormal function.
           If you want only the trainNum with its length less than 4,
           please set it to 1. With its default value(0), only trainNum with
           length more than 4 will be provided.
           For trainNum with length equals to 4, set it to 2.
        """
        queryUrl = self.apiAddress.format(trainKeyWord, dateStr)
        reqStr = self.proxyGet(queryUrl)
        isLocalTrain = 0
        # No data is replied.
        if reqStr is None:
            print 'trainHook.py: Warnging: Search for {} failed.'.format(trainKeyWord)
            self.thisClassFailList.append(trainKeyWord)
        else:
            # Process data in json.
            reqJson = json.loads(reqStr)
            for everyNum in reqJson["data"]:
                # Deal with trainNum on judgement.
                # Touch the top of L5(having length less than 5) trainNum list.
                if (judgement==1) and (len(everyNum['station_train_code']) > 4):
                    break
                # The base of M4(having length more than 4) trainNum list.
                elif not(judgement) and (len(everyNum['station_train_code']) < 5):
                    continue
                # Touch the top of local trains trainNum list.
                elif (judgement==2) and (isLocalTrain==1) and (everyNum['station_train_code'][0:2]!=trainKeyWord):
                    break
                # The base of local trains trainNum list.
                elif (judgement==2) and (isLocalTrain==0):
                    if everyNum['station_train_code'][0:2]==trainKeyWord:
                        isLocalTrain = 1
                else:
                    if judgement == 2:
                        trainClass = 'A'
                        trainNumber = everyNum['station_train_code']
                    else:
                        trainClass = everyNum['station_train_code'][0]
                        trainNumber = everyNum['station_train_code'][1:]
                    # The train is avilable, we only need to write the trainCode
                    if self.trainDb.verifyTrain(trainClass, int(trainNumber)):
                        self.codeDb.insert('{:0>8}'.format(str(trainVer)+trainClass + trainNumber),
                                           dateStr[0:4]+'-'+dateStr[4:6]+'-'+dateStr[6:8],
                                           everyNum['train_no'])
                    # Insert a new train to train table if it does not exist.
                    else:
                        self.trainDb.insertBase(int(trainNumber),
                                                int(trainNumber),
                                                trainClass,
                                                '{:0>8}'.format(str(trainVer)+trainClass + trainNumber),
                                                1)
                        self.codeDb.insert('{:0>8}'.format(str(trainVer)+trainClass + trainNumber),
                                           dateStr[0:4]+'-'+dateStr[4:6]+'-'+dateStr[6:8],
                                           everyNum['train_no'])

    def proxyGet(self, siteUrl):
        """Get reply from specified URL using proxy.
           Parameter siteUrl must be provided.
        """
        import urllib2
        res = None
        # Fail times limit
        fail = 0
        while (fail < 5):
            # Load a ramdom proxy
            proxyCount, randomProxy = self.proxyDb.random('HTTP')
            del proxyCount
            proxyUrl = "http://user:password@"+randomProxy[0]['address']+':'+str(randomProxy[0]['port'])
            proxySupport = urllib2.ProxyHandler({'http':proxyUrl})
            opener = urllib2.build_opener(proxySupport)
            urllib2.install_opener(opener)
            # Format a request
            request = urllib2.Request(siteUrl, headers=header)
            try:
                # Verfiy if the proxy is effective
                if ipVerify:
                    print 'trainHook.py: Info: IP address verification'
                    print urllib2.urlopen('http://icanhazip.com', timeout=4).read()[0:-1]
                # Send request to web api
                res = urllib2.urlopen(request, timeout=5).read()
            # Handle errors
            except Exception as error:
                print 'trainHook.py: Error: Request error occurs'
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

    def logFailTrain(self, fileName='failTrain.json'):
        """If too many errors occur in this train, log it to file.
        """
        with open(fileName, 'a') as fo:
            json.dump(self.thisClassFailList, fo)
        print 'trainHook.py: Info: Log failed trains done, with {} trains in it.'.format(len(self.thisClassFailList))

class test(object):
    
    def __init__(self):
        self.myhook = trainWebHook()

    def get(self, trainType):
        from datetime import date, timedelta
        myDate = date.today() + timedelta(days=1)
        if trainType == 'local' or trainType == 'l':
            self.myhook.catchLocal(myDate.strftime('%Y%m%d'))
        elif trainType == 'travel' or trainType == 't':
            self.myhook.catchTravel(myDate.strftime('%Y%m%d'))
        elif trainType == 'crossborder' or trainType == 'c':
            self.myhook.catchCrossborder(myDate.strftime('%Y%m%d'))
        else:
            self.myhook.catchNormal(myDate.strftime('%Y%m%d'))

if __name__ == "__main__":
    import sys
    trainType = sys.argv[1] if len(sys.argv) > 1 else 'normal'
    obj = test()
    obj.get(trainType)