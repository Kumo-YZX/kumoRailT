# Module Name: ProxyHook #
# Function: Search for proxy that are available. #
# Author: Kumo Lam(https://github.com/Kumo-YZX) #
# Last Edit: Feb/19/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('proxy', '../dbmaria/dbproxy/proxy.py')

test_url = 'https://search.12306.cn/search/v1/train/search?keyword=z1&date=20181228'

import proxy 

from bs4 import BeautifulSoup
import re
import urllib2
import json
import socket, httplib

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +\
          "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}


class ProxyData(object):

    def __init__(self):
        self.proxyDb = proxy.Table()
        print('proxyHook.py: Info: Init done.')
        self._proxy_list = []
        self._verify_list = []

    def get_proxy(self):
        """Get proxy text from file.
        """
        with open('proxy1.html', 'r') as fi:
            raw_data = fi.read()
        self._proxy_list = []
        for everyProxy in re.findall(r'<td class=tdl>.{358,418}<tr', raw_data):
            print(len(everyProxy))
            str_proxy = everyProxy+'>'
            print(str_proxy)
            son_obj = BeautifulSoup(str_proxy, 'html.parser')
            print(re.findall('&nbsp;(.*?)\\s<span>', str_proxy))
            category_list = str(son_obj.findAll('td')[4].string).split(', ')
            if 'HTTP' in category_list:
                support_http = 1
            else:
                support_http = 0
            if 'HTTPS' in category_list:
                support_https = 1
            else:
                support_https = 0

            son_dict = {"address": str(son_obj.find('td', attrs={"class":"tdl"}).string),
                        "port": int(son_obj.findAll('td')[1].string),
                        "country": str(re.findall('&nbsp;(.*?)\\s<span>', str_proxy)[0]),
                        "delay": int(son_obj.findAll('p')[0].string[0:-3]),
                        "state": str(son_obj.findAll('td')[5].string),
                        "fail_times": 0,
                        "connect_times": 0,
                        "http": support_http,
                        "https": support_https
                        }
            self._proxy_list.append(son_dict)
        print(len(self._proxy_list))

    def verify_proxy(self, file_name='proxy_list', site_url=test_url):
        """Verify if the proxy is available for specified site.
        """
        from datetime import date
        file_name = file_name + date.today().strftime('%Y%m%d') + '.json'
        proxy_no =0
        self._verify_list =[]
        while proxy_no < len(self._proxy_list):
            proxy_url = "http://user:password@"+self._proxy_list[proxy_no]['address']+':'+\
                        str(self._proxy_list[proxy_no]['port'])
            proxy_support = urllib2.ProxyHandler({'http':proxy_url})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
            request = urllib2.Request(site_url, headers=header)
            try:
                ip_str = urllib2.urlopen('http://icanhazip.com', timeout=4).read()[0:-1]
                print(ip_str)
                if ip_str == self._proxy_list[proxy_no]['address']:
                    print(urllib2.urlopen(request, timeout=8).read()[110:180])
                    self._verify_list.append(self._proxy_list[proxy_no])
                    if self.proxyDb.verify(self._proxy_list[proxy_no]['address'], self._proxy_list[proxy_no]['port']):
                        print('proxyHook.py: Info: This proxy already exists.')
                    else:
                        self.proxyDb.insert_dict(self._proxy_list[proxy_no])
                        print('proxyHook.py: Info: Find a new proxy.')
                else:
                    print('proxyHook.py: Info: IP verify fails..')
            # (urllib2.HTTPError, urllib2.URLError, socket.timeout, socket.error, httplib.BadStatusLine) as error:
            except Exception as error:
                print('proxyHook.py: Error: An error occurs with this proxy.')
                print(error)
                self._proxy_list[proxy_no]['state'] = 'No'
            finally:
                proxy_no +=1
                with open(file_name, 'w+') as fo:
                    json.dump(self._verify_list, fo)
                print('-'*36)


if __name__ == "__main__":
    proxyObj = ProxyData()
    proxyObj.get_proxy()
    proxyObj.verify_proxy()
