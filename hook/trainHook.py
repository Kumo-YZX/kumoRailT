# Module Name: TrainHook #
# Function: Import train&trainCode data from local file. #
# Author: Kumo Lam(https://github.com/Kumo-YZX) #
# Last Edit: Feb/20/2019 #
#

def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

load_module('train', '../dbmaria/dbp3/train.py')
load_module('trainCode', '../dbmaria/dbp3/trainCode.py')
load_module('proxy', '../dbmaria/dbproxy/proxy.py')

import train 
import trainCode
import proxy
import json, time

normalClass = ['G', 'D', 'C', 'Z', 'T', 'K']
specialClass = ['Y', 'P', 'S']
web_class = ['G', 'D', 'C', 'Z', 'T', 'K', 'O']
actual_class = ['G', 'D', 'C', 'Z', 'T', 'K', 'S', 'Y', 'P']
ipVerify = 1
trainVer = 1
header ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +\
         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
         "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}

class TrainWebHook(object):

    def __init__(self):
        self.apiAddress='https://search.12306.cn/search/v1/train/search?keyword={}&date={}'
        self.proxyDb = proxy.Table()
        self.trainDb = train.Table()
        self.codeDb = trainCode.Table()
        self.this_class_fail = []
        self.all_list = {}
        print 'trainHook.py: Info: TrainWebHook Init done'

    def catch_normal(self, date_str):
        """Catch all trainNums in normal class.
           Parameter date_str must be in YYYYMMDD format.
        """
        for everyClass in normalClass:
            self.this_class_fail = []
            # Verify numbers less than 1000
            for singleBit in range(1,10):
                # Send request and get reply using proxy
                self.req_rep(everyClass + str(singleBit), date_str, 1)
                print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(everyClass + str(singleBit))
                time.sleep(4)
            print 'trainHook.py: Info: Verify trainNums that less than 1k ends.'
            # Verify numbers more than 1000
            for multiBit in range(10, 100):
                # Send request and get reply using proxy.
                self.req_rep(everyClass + str(multiBit), date_str)
                print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(everyClass + str(multiBit))
                time.sleep(4)
            self.log_fail_train()
            print 'trainHook.py: Info: Verify trainNums that more than 1k ends.'

    def catch_local(self, date_str):
        """Catch all trainNums in local class.
           Local trains have their trainNum in 4-bits number only.
        """
        self.this_class_fail = []
        # Use a 2-bit number as keyword.
        for multiBit in range(10, 100):
            self.req_rep(str(multiBit), date_str, 2)
            print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(str(multiBit))
            time.sleep(4)
        self.log_fail_train()
        print 'trainHook.py: Info: Verify local trains ends.'

    def catch_travel(self, date_str):
        """Catch all trainNums of travel trains.
           Travel trains have their trainNums in Pxxx format.
        """
        self.this_class_fail = []
        # Use Y1-Y9 as keywords.
        train_class = 'Y'
        for singleBit in range(1,10):
            self.req_rep(train_class + str(singleBit), date_str, 1)
            print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(train_class + str(singleBit))
            time.sleep(4)
        self.log_fail_train()
        print 'trainHook.py: Info: Verify travel trains ends.'

    def catch_cross_border(self, date_str):
        """Catch all trainNums of Cross-border trains(Kowloon-Shanghai/Beijing Through Train)
           TrainNums contains P97-P100 only, using P as keyword directly.
        """
        self.this_class_fail = []
        train_class = 'P'
        self.req_rep(train_class, date_str, 1)
        print 'trainHook.py: Info: Search for keyWord [{}] done.'.format(train_class)
        self.log_fail_train()
        print 'trainHook.py: Info: Verify cross-border trains ends.'

    def req_rep(self, train_key_word, date_str, judgement=0):
        """Send request and get reply from API.
           Divided from catch_normal function.
           If you want only the trainNum with its length less than 4,
           please set it to 1. With its default value(0), only trainNum with
           length more than 4 will be provided.
           For trainNum with length equals to 4, set it to 2.
        """
        query_url = self.apiAddress.format(train_key_word, date_str)
        req_str = self.proxy_get(query_url)
        is_local_train = 0
        # Replied without train data.
        if req_str is None or "data" not in req_str:
            print 'trainHook.py: Warning: Search for {} failed.'.format(train_key_word)
            self.this_class_fail.append(train_key_word)
        else:
            # Process data in json.
            req_json = json.loads(req_str)
            for everyNum in req_json["data"]:
                # Deal with trainNum on judgement.
                # Touch the top of L5(having length less than 5) trainNum list.
                if (judgement==1) and (len(everyNum['station_train_code']) > 4):
                    break
                # The base of M4(having length more than 4) trainNum list.
                elif not judgement and (len(everyNum['station_train_code']) < 5):
                    continue
                # Touch the top of local trains trainNum list.
                elif (judgement==2) and (is_local_train==1) and (everyNum['station_train_code'][0:2]!=train_key_word):
                    break
                # The base of local trains trainNum list.
                elif (judgement==2) and (is_local_train==0):
                    if everyNum['station_train_code'][0:2]==train_key_word:
                        is_local_train = 1
                else:
                    if judgement == 2:
                        train_class = 'A'
                        train_number = everyNum['station_train_code']
                    else:
                        train_class = everyNum['station_train_code'][0]
                        train_number = everyNum['station_train_code'][1:]
                    # The train is available, we only need to write the trainCode
                    if self.trainDb.verify_train(train_class, int(train_number)):
                        self.codeDb.insert('{:0>8}'.format(str(trainVer)+train_class + train_number),
                                           date_str[0:4]+'-'+date_str[4:6]+'-'+date_str[6:8],
                                           everyNum['train_no'])
                    # Insert a new train to train table if it does not exist.
                    else:
                        self.trainDb.insert_base(int(train_number),
                                                int(train_number),
                                                train_class,
                                                '{:0>8}'.format(str(trainVer)+train_class + train_number),
                                                1)
                        self.codeDb.insert('{:0>8}'.format(str(trainVer)+train_class + train_number),
                                           date_str[0:4]+'-'+date_str[4:6]+'-'+date_str[6:8],
                                           everyNum['train_no'])

    def proxy_get(self, site_url):
        """Get reply from specified URL using proxy.
           Parameter site_url must be provided.
        """
        import urllib2
        res = None
        # Fail times limit
        fail = 0
        while fail < 5:
            # Load a random proxy
            proxy_count, random_proxy = self.proxyDb.random('HTTP')
            del proxy_count
            proxy_url = "http://user:password@"+random_proxy[0]['address']+':'+str(random_proxy[0]['port'])
            proxy_support = urllib2.ProxyHandler({'http':proxy_url})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
            # Format a request
            request = urllib2.Request(site_url, headers=header)
            try:
                # Verify whether the proxy is effective
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
                random_proxy[0]['fail_times'] = random_proxy[0]['fail_times'] + 1
            # write feedback to proxy database.
            finally:
                random_proxy[0]['connect_times'] = random_proxy[0]['connect_times'] + 1
                self.proxyDb.update_status(random_proxy[0]['proxy_id'],
                                          random_proxy[0]['connect_times'],
                                          random_proxy[0]['fail_times'])
                if res is not None:
                    break
        return res

    def log_fail_train(self, file_name='fail_train.json'):
        """If too many errors occur on this train, log it to file.
        """
        with open(file_name, 'a') as fo:
            json.dump(self.this_class_fail, fo)
        print 'trainHook.py: Info: Log failed trains done, with {} trains in it.'.format(len(self.this_class_fail))

    def load_local_file(self, file_name="train_list.json"):
        """

        :param file_name: String
        :return: None
        """
        with open(file_name, 'r') as fi:
            self.all_list = json.load(fi)


    def import_form_file(self, date, train_ver=1):
        """

        :param date:
        :param train_ver:
        :return:
        """
        if date in self.all_list:
            for every_class in web_class:
                # Catch the list of specified date and class.
                train_list = self.all_list[date][every_class]
                for every_train in train_list:
                    # Catch train_no.
                    train_no = every_train['station_train_code'].split('(')[0]
                    train_str = ''
                    flag = 0
                    # Catch train_str from long big string.
                    for every_char in every_train['train_no'][2:-2]:
                        if every_char != '0':
                            flag = 1
                        if flag == 1:
                            train_str = train_str + every_char
                    # Care about the basic train number.
                    if train_no == train_str:
                        if train_no[0] in actual_class:
                            train_num = int(train_no[1:])
                            train_class = train_no[0]
                        else:
                            train_num = int(train_no)
                            train_class = 'A'

                        internal_str = '{:0>8}'.format(str(train_ver) + train_class + str(train_num))
                        if not self.trainDb.verify_str(internal_str):
                            # Invalidate the old version if it exists.
                            self.trainDb.update_status(train_num, train_class, False)
                            print("Now: Insert: {}".format(internal_str))
                            # Insert the new version.
                            self.trainDb.insert_base(train_num, train_num, train_class, internal_str, True)

                        if not self.codeDb.verify(internal_str, date):
                            self.codeDb.insert(internal_str, date, every_train['train_no'])

                for every_train in train_list:
                    train_no = every_train['station_train_code'].split('(')[0]
                    train_str = ''
                    flag = 0
                    for every_char in every_train['train_no'][2:-2]:
                        if every_char != '0':
                            flag = 1
                        if flag == 1:
                            train_str = train_str + every_char
                    # Care about the special number.
                    # This module will update train_num1 if the train have another alias.
                    if train_no != train_str:
                        if train_no[0] in actual_class:
                            train_num = int(train_no[1:])
                            actual_num = int(train_str[1:])
                            train_class = train_no[0]
                        else:
                            train_num = int(train_no)
                            actual_num = int(train_str)
                            train_class = 'A'
                        print("Now: Update: {}, {}".format(actual_num, train_class))
                        self.trainDb.update_base(actual_num, train_num, train_class)

def test_import_file():
    from datetime import date, timedelta
    my_date = date.today() + timedelta(days=1)
    import_obj = TrainWebHook()
    import_obj.load_local_file()
    import_obj.import_form_file(my_date.strftime('%Y-%m-%d'))


class Test(object):
    
    def __init__(self):
        self.my_hook = TrainWebHook()

    def get(self, train_type):
        from datetime import date, timedelta
        my_date = date.today() + timedelta(days=1)
        if train_type == 'local' or train_type == 'l':
            self.my_hook.catch_local(my_date.strftime('%Y%m%d'))
        elif train_type == 'travel' or train_type == 't':
            self.my_hook.catch_travel(my_date.strftime('%Y%m%d'))
        elif train_type == 'cross-border' or train_type == 'c':
            self.my_hook.catch_cross_border(my_date.strftime('%Y%m%d'))
        elif train_type == 'normal' or train_type == 'n':
            self.my_hook.catch_normal(my_date.strftime('%Y%m%d'))
        else:
            test_import_file()

if __name__ == "__main__":
    import sys
    input_type = sys.argv[1] if len(sys.argv) > 1 else 'file'
    obj = Test()
    obj.get(input_type)