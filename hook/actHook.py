# Module Name: Actual Arrival Hook
# Function: Catch Actual Arrival info from web.
# Author: Kumo Lam (https://github.com/Kumo-YZX)
# Date: Mar/18/2019
# print("hook/actHook.py: Info: ")


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('subArr', '../dbmaria/dbp5/subArr.py')
load_module('actArr', '../dbmaria/dbp5/actArr.py')
load_module('staInfo', '../dbmaria/dbp1/staInfo.py')
load_module('train', '../dbmaria/dbp3/train.py')
load_module('tool', '../tool/tool.py')
load_module('proxy', '../dbmaria/dbproxy/proxy.py')
load_module('config', '../config.py')
import subArr
import actArr
import tool
import proxy
import config
import train
import staInfo

header = config.header
arr_info_url = config.arr_info_url
verify = config.proxy_verify


class Hook(object):

    def __init__(self):
        self.subdb = subArr.Table()
        self.actdb = actArr.Table()
        self.proxydb = proxy.Table()
        self.stadb = staInfo.Table()
        self.traindb = train.Table()
        self.web_raw = None
        print("hook/actHook.py: Info: ActHook Init done.")

    def pre_set_sch(self):
        """
        Set Schedule Arrival information for the progress to catch.
        SchArrs of today will be set.
        :return: Int, Nums of Arrivals that have been Set.
        """
        import json
        import datetime
        sub_amount = 0
        date_today = datetime.datetime.today()
        str_today = date_today.strftime("%Y-%m-%d")
        with open("act_status.json", "r") as fi:
            list_act_status = json.load(fi)
        if str_today in list_act_status:
            print("hook/actHook.py: Info: No Arrival need to be imported.")
        # Today's log haven't been set
        else:
            sub_amount, sub_list = self.subdb.catch()
            # Import all SubArrs
            for every_sub in sub_list:
                self.actdb.new(every_sub["sub_arr_id"], date_today)
            print("hook/actHook.py: " +
                  "Info: {} Arrival(s) have been imported.".format(sub_amount))
            list_act_status.append(str_today)
            with open("act_status.json", "w") as fo:
                json.dump(list_act_status, fo)
        return sub_amount

    def get_act(self, use_proxy=1):
        """
        Grab actual Arrival time from the web.
        Amount of grabbed data will be returned.
        :return: Integer
        """
        import datetime
        import random
        import re
        date_today = datetime.datetime.today()
        date_yesterday = date_today + datetime.timedelta(days=-1)
        # Is deadline Essential???
        deadline = tool.str2int(datetime.datetime.now().strftime("%H:%M"))
        deadline = deadline - 5 if deadline > 4 else 0
        # Arrivals of today
        today_arr_status, today_arr_info = self.actdb.catch(date_today, deadline)
        # ...and of yesterday
        yesterday_arr_status, yesterday_arr_info =\
            self.actdb.catch(date_yesterday, 1440)
        # These arrivals are too early to get any information.
        # Essential ???
        # Do not give up any arrival and they will be found finally...
        for every_arr in today_arr_info:
            if every_arr["schedule_time"] < deadline - 65:
                self.actdb.write(every_arr["act_arr_id"],
                                 delay=every_arr["delay"],
                                 update_mark=1)
                del every_arr

        for every_arr in yesterday_arr_info:
            if every_arr["schedule_time"] < 1380 or deadline > 65:
                self.actdb.write(every_arr["act_arr_id"],
                                 delay=every_arr["delay"],
                                 update_mark=1)
                del every_arr

        today_arr_info = list(today_arr_info) + list(yesterday_arr_info)
        for every_arr in today_arr_info:
            arr_status, arr_detail =\
                self.subdb.search_by_id(every_arr["sub_arr_id"])
            if arr_status:
                arr_station_status, arr_station_detail =\
                    self.stadb.search('sta_tele', arr_detail[0]["sta_tele"])
                station_name = arr_station_detail[0]["sta_cn"].decode("hex").decode('utf8')
                arr_train_status, arr_train_detail =\
                    self.traindb.search('train_str', arr_detail[0]["train_str"])
                # Correct train Class
                if arr_train_detail[0]["train_class"] == "A":
                    train_num = str(arr_train_detail[0]["train_num0"])
                else:
                    train_num = arr_train_detail[0]["train_class"] + \
                        str(arr_train_detail[0]["train_num0"])
                # In fact, date and time_tag effect nothing.
                date_str = date_today.strftime("%Y-%m-%d")
                time_tag = datetime.datetime.now().strftime("%s") +\
                    str(random.randint(1000, 9999))
                print("hook/actHook.py: Debug: Station Name " +
                      "GBK: {} UTF8: {}".format(tool.encode_gbk(station_name),
                                                tool.encode_utf(station_name)))
                if use_proxy:
                    self.proxy_get(tool.encode_gbk(station_name),
                                   tool.encode_utf(station_name),
                                   train_num,
                                   date_str,
                                   time_tag)
                else:
                    self.local_get(tool.encode_gbk(station_name),
                                   tool.encode_utf(station_name),
                                   train_num,
                                   date_str,
                                   time_tag)
                if self.web_raw is None:
                    print("hook/actHook.py: Warning: Connection error occurs.")
                else:
                    print self.web_raw
                    arrival_time_str = re.findall('\\d{2}:\\d{2}', self.web_raw)
                    if len(arrival_time_str):
                        # Actual arr time
                        arrival_time_int = tool.str2int(arrival_time_str[0])
                        now_int =\
                            tool.str2int(datetime.datetime.now().strftime("%H:%M"))
                        # The train has arrived.
                        # It is better to handle cross-day arrival individually...
                        # Deep into each condition!!!
                        arrival_flag = now_int - arrival_time_int
                        if arrival_flag > 0 or arrival_flag < -720:
                            if arrival_time_int - arr_detail[0]["schedule_time"] < -720:
                                self.actdb.write(every_arr["act_arr_id"],
                                                 1440 - arr_detail[0]["schedule_time"] +
                                                 arrival_time_int,
                                                 1)
                            else:
                                self.actdb.write(every_arr["act_arr_id"],
                                                 arrival_time_int -
                                                 arr_detail[0]["schedule_time"],
                                                 1)
                        # Warning: The delay item may contain wrong data.
                        # For debug only and will not be shown.
                        else:
                            self.actdb.write(every_arr["act_arr_id"],
                                             arrival_time_int -
                                             arr_detail[0]["schedule_time"],
                                             0)
                        print("hook/actHook.py: Info: New data: " +
                              " Sub-Arrival: {} ".format(arr_detail[0]["sub_arr_id"]) +
                              " Station: {}".format(arr_detail[0]["sta_tele"]) +
                              " Train: {}".format(arr_detail[0]["train_str"]) +
                              " Schedule: {} ".format(arr_detail[0]["schedule_time"]) +
                              " Actual: {}".format(arrival_time_int))
                    else:
                        print("hook/actHook.py: Info: Useless web data")
            else:
                print("hook/actHook.py: Warning: Arrival does not exist.")
        print("hook/actHook.py: Info: End of this Round.")

    def proxy_get(self, sta_gbk, sta_utf, train_num, date_str, time_tag):
        """
        Catch web data using proxy.
        Raw data on the web will be returned.
        :param sta_gbk: String
        :param sta_utf: String
        :param train_num: String
        :param date_str: String
        :param time_tag: String
        :return: String
        """
        import urllib2
        res = None
        # Fail time count.
        fail = 0
        while fail < 5:
            # Load a random proxy
            proxy_count, random_proxy = self.proxydb.random('HTTP')
            del proxy_count
            proxy_url = "http://user:password@"+random_proxy[0]['address']+':' +\
                        str(random_proxy[0]['port'])
            proxy_support = urllib2.ProxyHandler({'http': proxy_url})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
            # Form a request
            request = urllib2.Request(arr_info_url.format(sta_gbk,
                                                          train_num,
                                                          date_str,
                                                          sta_utf,
                                                          time_tag),
                                      headers=header)
            try:
                if verify:
                    print urllib2.urlopen('http://icanhazip.com', timeout=4).read()[0:-1]
                res = urllib2.urlopen(request, timeout=5).read()
            # Handle errors
            except Exception as error:
                print "hook/actHook.py: Error: Request error occurs"
                print error
                fail = fail + 1
                random_proxy[0]['fail_times'] = random_proxy[0]['fail_times'] + 1
            # write feedback to proxy database.
            finally:
                random_proxy[0]['connect_times'] = random_proxy[0]['connect_times'] + 1
                self.proxydb.update_status(random_proxy[0]['proxy_id'],
                                           random_proxy[0]['connect_times'],
                                           random_proxy[0]['fail_times'])
                if res is not None:
                    break
        self.web_raw = res
        return res

    def local_get(self, sta_gbk, sta_utf, train_num, date_str, time_tag):
        """
        Catch web data without proxy(locally).
        Raw data on the web will be returned.
        :param sta_gbk: String
        :param sta_utf: String
        :param train_num: String
        :param date_str: String
        :param time_tag: String
        :return: String
        """
        res = None
        import urllib2
        request = urllib2.Request(arr_info_url.format(sta_gbk,
                                                      train_num,
                                                      date_str,
                                                      sta_utf,
                                                      time_tag),
                                  headers=header)
        try:
            res = urllib2.urlopen(request, timeout=5).read()
        except Exception as error:
            print "hook/actHook.py: Error: Request error occurs"
            print error
        self.web_raw = res
        return res


def run():
    import json
    import time
    my_hook = Hook()
    act_control = 1
    while act_control:
        my_hook.pre_set_sch()
        my_hook.get_act(use_proxy=1)
        time.sleep(40)
        with open("act_control.json", "r") as fi:
            act_control = json.load(fi)["control"]


if __name__ == "__main__":
    run()
