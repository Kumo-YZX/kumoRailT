#---#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('proxy', '../dbmaria/proxy.py')

import proxy 

from bs4 import BeautifulSoup
import re
import urllib2
import json
import socket, httplib

header ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
         "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}

class proxyData(object):

    def __init__(self):
        self.proxyDb = proxy.table()
        print 'PROXY HOOK INIT'

    def getProxy(self):
        with open('proxy1.html', 'r') as fi:
            rawData = fi.read()
        self._proxyList =[]
        for everyProxy in re.findall(r'<td class=tdl>.{358,418}<tr', rawData):
            print len(everyProxy)
            strProxy =everyProxy+'>'
            print strProxy
            sonObj =BeautifulSoup(strProxy, 'html.parser')
            print re.findall('&nbsp;(.*?)\\s<span>', strProxy)
            categoryList = str(sonObj.findAll('td')[4].string).split(', ')
            if 'HTTP' in categoryList:
                httpSupport = 1
            else:
                httpSupport = 0
            if 'HTTPS' in categoryList:
                httpsSupport = 1
            else:
                httpsSupport = 0

            sonDict ={"address":str(sonObj.find('td', attrs={"class":"tdl"}).string),
                    "port":int(sonObj.findAll('td')[1].string),
                    "country":str(re.findall('&nbsp;(.*?)\\s<span>', strProxy)[0]),
                    "delay":int((sonObj.findAll('p')[0].string)[0:-3]),
                    "state":str(sonObj.findAll('td')[5].string),
                    "failTimes":0,
                    "connectTimes":0,
                    "http":httpSupport,
                    "https":httpsSupport
                    }
            self._proxyList.append(sonDict)
        print len(self._proxyList)

    def verifyProxy(self, fileName='proxyList'):
        from datetime import date
        fileName = fileName + date.today().strftime('%Y%m%d') + '.json'
        proxyNo =0
        self._verifyList =[]
        while proxyNo <len(self._proxyList):
            proxyUrl = "http://user:password@"+self._proxyList[proxyNo]['address']+':'+str(self._proxyList[proxyNo]['port'])
            proxySupport = urllib2.ProxyHandler({'http':proxyUrl})
            opener = urllib2.build_opener(proxySupport)
            urllib2.install_opener(opener)
            request =urllib2.Request('http://mobile.12306.cn/weixin/czxx/queryByTrainNo?train_no=24000000Z10D&from_station_telecode=BBB&to_station_telecode=BBB&depart_date=2018-08-28',
                                    headers=header)
            try:
                ipStr = urllib2.urlopen('http://icanhazip.com', timeout=4).read()[0:-1]
                print ipStr
                if ipStr == self._proxyList[proxyNo]['address']:
                    print (urllib2.urlopen(request, timeout=8).read())[110:180]
                    self._verifyList.append(self._proxyList[proxyNo])
                    if self.proxyDb.verify(self._proxyList[proxyNo]['address'], self._proxyList[proxyNo]['port']):
                        print 'THIS PROXY ALREADY EXISTS'
                    else:
                        self.proxyDb.insertDict(self._proxyList[proxyNo])
                        print 'NEW PROXY INSERTED'
                else:
                    print 'IP VERIFY FAILED'
            except Exception as error:#(urllib2.HTTPError, urllib2.URLError, socket.timeout, socket.error, httplib.BadStatusLine) as error:
                print 'ERROR OCCURS'
                print error
                self._proxyList[proxyNo]['state'] = 'No'
            finally:
                proxyNo +=1
                with open(fileName, 'w+') as fo:
                    json.dump(self._verifyList, fo)
                print '-'*36

if __name__ == "__main__":
    proxyObj = proxyData()
    proxyObj.getProxy()
    proxyObj.verifyProxy()