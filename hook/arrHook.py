# Module Name: ArrHook #
# Function: Import train arrival data form web page. #
# Author: Kumo Lam(https://github.com/Kumo-YZX) #
# Last Edit: Feb/27/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('arrival', '../dbmaria/dbp4/arrival.py')
load_module('train', '../dbmaria/dbp3/train.py')
load_module('train_code', '../dbmaria/dbp3/trainCode.py')
load_module('staInfo', '../dbmaria/dbp1/staInfo.py')
load_module('proxy', '../dbmaria/dbproxy/proxy.py')
load_module('tool', '../tool/tool.py')

import arrival, train, train_code
import staInfo, proxy, tool
import json

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}
arrUrl = "http://mobile.12306.cn/weixin/czxx/queryByTrainNo?train_no={}" +\
         "&from_station_telecode=BBB&to_station_telecode=BBB&depart_date={}"
verify = 1


class TrainArrHook(object):

    def __init__(self):
        self.arrivalDb = arrival.Table()
        self.trainDb = train.Table()
        self.codeDb = train_code.Table()
        self.stationDb = staInfo.Table()
        self.proxyDb = proxy.Table()
        print 'arrHook.py: Info: trainArrHook Init done.'

    def add_train(self, train_str, date):
        """Add all arrival data of a train.
           Parameter date should be in YYYY-MM-DD format.
        """
        import time
        # Verify the operation status of specified train.
        # In fact, any day in operation is ok to catch arrival data of
        # this train(different train_str marks different train).
        code_status, code_info = self.codeDb.search(train_str, date)
        if code_status:
            # Get arrival data by proxy_get function.
            raw_arr_data = self.proxy_get(code_info[0]['train_code'], code_info[0]['depart_date'])
            if raw_arr_data is not None:
                arr_data = json.loads(raw_arr_data)
                arr_list = arr_data['data']['data']
                final_list = []
                if len(arr_list):
                    # Replace arrive time of depart station and depart time of terminal station with 2401.
                    arr_list[0]['arrive_time'] = '24:01'
                    arr_list[-1]['start_time'] = '24:01'
                    # Write every arrival to database.
                    for everyArrival in arr_list:
                        station_status, station_info = \
                            self.stationDb.search('sta_cn', everyArrival['station_name'].encode('utf8').encode('hex'))
                        if station_status:
                            sta_tele = station_info[0]['sta_tele']
                        else:
                            # The arrive station haven't been recorded.
                            special_station_count = self.stationDb.verify_special(10001)
                            sta_tele = '{:0>3}'.format(special_station_count+1)
                            self.stationDb.insert({'sta_cn': everyArrival['station_name'].encode('utf8').encode('hex'),
                                                   'sta_tele': sta_tele,
                                                   'sta_py': '0000',
                                                   'sta_num': special_station_count+10001})
                            print 'INSERT NEW STATION ' + everyArrival['station_name']
                        # print sta_tele
                        # Transfer time into integer format.
                        arr_time = tool.str2int(everyArrival['arrive_time'])
                        dep_time = tool.str2int(everyArrival['start_time'])

                        final_list.append({"sta_tele": sta_tele,
                                           "sta_rank": int(everyArrival['station_no']),
                                           "train_str": train_str,
                                           "arr_time": arr_time,
                                           "dep_time": dep_time})
                    del arr_data, arr_list
                    arr_date = 0
                    dep_date = 1
                    # Calculate the date of every arrival.
                    for arrivalNo in range(1, len(final_list)):
                        if final_list[arrivalNo]['arr_time'] < final_list[arrivalNo-1]['arr_time']:
                            arr_date = arr_date + 1
                        if final_list[arrivalNo]['dep_time'] < final_list[arrivalNo-1]['dep_time']:
                            dep_date = dep_date + 1
                        final_list[arrivalNo]['arr_date'] = arr_date
                        final_list[arrivalNo]['dep_date'] = dep_date
                    final_list[0]['arr_date'] = 1
                    final_list[0]['dep_date'] = 1

                    # Write them to database.
                    for everyArrival in final_list:
                        self.arrivalDb.insert_dict(everyArrival)

                    write_log('SUCCESS : ' + train_str)
                    print 'arrHook.py: Info: Add arrival successfully.'
                else:
                    print 'arrHook.py: Info: This train exists, but do not have arrival data.'
                time.sleep(1)
            else:
                # Log failed trains.
                # But do not write to vacancyFile. To check failed trains, please use CHECK function.
                write_bc(train_str)
                write_log('TOO MANY BAD CONNECTIONS : ' + train_str)
                print 'arrHook.py: Warning: Too many bad connections with [{}].'.format(train_str)

        else:
            print 'arrHook.py: Warning: This train does not operate on {}.'.format(date)

        print '-'*36

    def proxy_get(self, train_code, date):
        """Get reply from specified URL using proxy.
           Parameter must be provided.
        """
        import urllib2
        res = None
        # Fail time count.
        fail = 0
        while fail < 5:
            # Load a random proxy
            proxy_count, random_proxy = self.proxyDb.random('HTTP')
            del proxy_count
            proxy_url = "http://user:password@"+random_proxy[0]['address']+':'+str(random_proxy[0]['port'])
            proxy_support = urllib2.ProxyHandler({'http': proxy_url})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
            # Format a request
            request = urllib2.Request(arrUrl.format(train_code, date), headers=header)
            try:
                if verify:
                    print urllib2.urlopen('http://icanhazip.com', timeout=4).read()[0:-1]
                res = urllib2.urlopen(request, timeout=5).read()
            # Handle errors
            except Exception as error:
                print 'arrHook.py: Error: Request error occurs'
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

    def region_get(self, start, end, train_class):
        """Get all arrivals in provided region.
           Parameter start and end marks the base and top of region.
        """
        from datetime import date, timedelta
        import time
        date_tomorrow = date.today() + timedelta(days=1)
        region_status, train_list = self.trainDb.search_list(start, end, train_class)
        print 'arrHook.py: Info: There are {} trains in this region.'.format(region_status)
        for everyTrain in train_list:
            print 'arrHook.py: Info: We are now import {}.'.format(everyTrain['train_str'])
            self.add_train(everyTrain['train_str'], date_tomorrow.strftime("%Y-%m-%d"))
            time.sleep(1)

    def get_missing_train(self, vacancy_train_file='vacancy_list.json'):
        """Add arrivals of failed trains.
           Parameter file name are optional.
        """
        from datetime import date, timedelta
        import time
        date_tomorrow = date.today() + timedelta(days=1)
        with open(vacancy_train_file, 'r') as fi:
            vacancy_list = json.load(fi)
        print 'arrHook.py: Info: There are {} trains in this region.'.format(len(vacancy_list))
        for everyTrain in vacancy_list:
            print 'arrHook.py: Info: We are now import [{}].'.format(everyTrain)
            self.add_train(everyTrain, date_tomorrow.strftime("%Y-%m-%d"))
            time.sleep(1)

    def check(self, train_class, start=0, end=10000):
        """Check the arrival-catching status of every train.
           If the train don't have any arrival, mark it as failed and register to file.
        """
        region_status, train_list = self.trainDb.search_list(start, end, train_class)
        print 'arrHook.py: Info: We need to check {} trains.'.format(region_status)
        vacancy_list = []
        for everyTrain in train_list:
            if not(self.arrivalDb.verify_arrival(everyTrain['train_str'])):
                vacancy_list.append(everyTrain['train_str'])
                print 'arrHook.py: Info: Arrival of {} do not exist.'.format(everyTrain['train_str'])
        
        with open('vacancy_list.json', 'a+') as fo:
            json.dump(vacancy_list, fo)


def write_log(info, log_file='arr_hook_log.txt'):
    import datetime
    with open(log_file, 'a+') as fo:
        fo.write(datetime.datetime.now().strftime('%Y%m%d%H%M%S') + ' - ' + info)


def write_bc(train_str, bc_file='bc_train.txt'):
    with open(bc_file, 'a+') as fo:
        fo.write(train_str+',')


class Run(object):
    
    def __init__(self):
        self.obj = TrainArrHook()

    def add(self):
        """Add new arrivals in start_num(included) and end_num(included) region.
        """
        start_num = raw_input('start_num(included):')
        end_num = raw_input('end_num(not included):')
        train_class = raw_input('train_class:')
        self.obj.region_get(int(start_num), int(end_num), train_class)

    def check(self):
        """Check arrivals.
        """
        start_num = raw_input('start_num:')
        end_num = raw_input('end_num:')
        train_class = raw_input('train_class:')
        self.obj.check(train_class, int(start_num), int(end_num))
    
    def add_miss(self):
        self.obj.get_missing_train()


# Run the script.
if __name__ == "__main__":
    import sys
    myObj = Run()
    if len(sys.argv) == 1:
        myObj.add()
    else:
        if sys.argv[1] == 'add':
            myObj.add()
        elif sys.argv[1] == 'che':
            myObj.check()
        elif sys.argv[1] == 'ams':
            myObj.add_miss()
