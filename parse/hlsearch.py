# Module Name: hlsearch(high-level search) #
# Function: Connect the database and return info to the parse module. #
# Author: Kumo Lam(https://github.com/Kumo-YZX) #
# Last Edit: Mar/16/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('arrival', '../dbmaria/dbp4/arrival.py')
load_module('staInfo', '../dbmaria/dbp1/staInfo.py')
load_module('trainCode', '../dbmaria/dbp3/trainCode.py')
load_module('train', '../dbmaria/dbp3/train.py')
load_module('seq', '../dbmaria/dbp2/seq.py')
load_module('depot', '../dbmaria/dbp2/depot.py')
load_module('subArr', '../dbmaria/dbp5/subArr.py')
load_module('actArr', '../dbmaria/dbp5/actArr.py')
load_module('tool', '../tool/tool.py')
load_module('depotHook', '../hook/depotHook.py')

# Do not import all modules here.
# Import them in essential place.
import arrival, staInfo, trainCode, train, seq, depot
import tool
import chnword
import depotHook

actual_class = ['G', 'D', 'C', 'Z', 'T', 'K', 'S', 'Y', 'P']


class Hls(object):

    def __init__(self):
        print('hlsearch.py: Info: High level search loaded.')

    def seqs(self, train_num, train_class):
        """Provide the sequence and department & terminal station of a train.
           Parameter train_num and train_class must be provided.
           train_num can be in any(string/integer) format.
           Return value(Reply) is in Chn format.
        """
        reply = train_class.upper() + str(train_num) + ' '
        # Initialize the train/arrival/station table object.
        train_db = train.Table()
        arrival_table = arrival.Table()
        sta_table = staInfo.Table()
        # Search for the train.
        train_status, train_info = train_db.search_dual(train_class, str(train_num))
        if not train_status:
            print('hlseach.py: Warning: This train does not exist.')
            return reply + chnword.trainDoNotExist.decode('hex')
        train_status, arr_info = arrival_table.search(train_info[0]['train_str'])
        if not train_status:
            return chnword.trainExistsButNoArrival.decode('hex')
        # Search for the dep & arr station of this train.
        first_status, first_info = sta_table.search('sta_tele', arr_info[0]['sta_tele'])
        last_status, last_info = sta_table.search('sta_tele', arr_info[-1]['sta_tele'])
        reply = reply + first_info[0]['sta_cn'].decode('hex') + '-' + last_info[0]['sta_cn'].decode('hex') + '\n'
        del train_status, first_status, last_status, arr_info
        del arrival_table, sta_table
        # Initialize the sequence/depot table object.
        seq_db = seq.Table()
        depot_db = depot.Table()
        # Search for the depot & sequence data.
        seq_status, seq_info = seq_db.search('seq_id', train_info[0]['seq_id'])
        reply = reply + chnword.EMUType.decode('hex') + ':' + seq_info[0]['emu_type'].decode('hex') + '\n'
        staff_status, staff_info = depot_db.search(int(seq_info[0]['staff']))
        vehicle_status, vehicle_info = depot_db.search(int(seq_info[0]['depot']))
        reply = reply + staff_info[0]['depot_cn'].decode('hex') + chnword.staffDep.decode('hex') + ' '
        reply = reply + vehicle_info[0]['depot_cn'].decode('hex') + chnword.vehicleDep.decode('hex') + '\n'
        del staff_status, staff_info, vehicle_status, vehicle_info
        seq_search_status, seq_search_trains = train_db.search('seq_id', train_info[0]['seq_id'])
        del seq_search_status, seq_status
        from operator import itemgetter
        reply = reply + chnword.seqNo.decode('hex') + ':'
        # Sort the trains in the same sequence and format the reply.
        seq_search_trains = sorted(seq_search_trains, key=itemgetter('seq_rank'))
        for everyTrain in seq_search_trains:
            reply = reply + tool.correctClass(everyTrain['train_class']).encode('utf8')
            reply = reply + str(everyTrain['train_num0'])
            if everyTrain['train_num0'] != everyTrain['train_num1']:
                train_number_string_0 = str(everyTrain['train_num0'])
                train_number_string_1 = str(everyTrain['train_num1'])
                reply = reply + '/'
                if len(train_number_string_0) == len(train_number_string_1):
                    for location in range(len(train_number_string_0)):
                        if train_number_string_1[location] != train_number_string_0[location]:
                            reply = reply + train_number_string_1[location]
                else:
                    reply = reply + train_number_string_1
            reply = reply + '-'

        return reply[0:-1]

    def arrs(self, train_num, train_class):
        """Get all the arrivals of a train.
           Parameter train_num and train_class must be provided.
           train_num can be in any(string/integer) format.
           Return value(Reply) is in Chn format.
        """
        # Initialize the train/arrival/station table object.
        train_db = train.Table()
        arrival_db = arrival.Table()
        station_db = staInfo.Table()
        # Search for train data.
        train_status, train_info = train_db.search_dual(train_class, int(train_num))
        if not train_status:
            print('hlseach.py: Warning: This train does not exist.')
            return chnword.trainDoNotExist.decode('hex')
        if train_class == 'A':
            train_class = ''
        reply = chnword.trainNo.decode('hex') + ':' + train_class.upper() + str(train_num) + '\n'
        # Search for all the arrivals.
        train_status, arr_info = arrival_db.search(train_info[0]['train_str'])
        if not train_status:
            return chnword.trainExistsButNoArrival.decode('hex')
        del train_status
        # Format them.
        for everyArr in arr_info:
            station_status, station_info = station_db.search('sta_tele', everyArr['sta_tele'])
            reply = reply + station_info[0]['sta_cn'].decode('hex') + (8-len(station_info[0]['sta_cn'])/3)*' '
            if everyArr['arr_time'] == 1441:
                reply = reply + '-----' + ' '
            else:
                reply = reply + tool.int2str(everyArr['arr_time']) + ' '

            if everyArr['dep_time'] == 1441:
                reply = reply + '-----' + '\n'
            else:
                reply = reply + tool.int2str(everyArr['dep_time']) + '\n'
        del station_status

        return reply[0:-1]

    def dbs(self, sta_pinyin):
        """Search for the telecode of a station.
           Parameter sta_pinyin is the first character of the station's pinyin.
        """
        station_db = staInfo.Table()
        station_status, station_info = station_db.search('sta_py', sta_pinyin.lower())
        if not station_status:
            print('hlseach.py: Warning: This station does not exist.')
            return chnword.stationDoNotExist.decode('hex')
        reply = ''
        for everySta in station_info:
            reply = reply + chnword.station.decode('hex') + ':' + everySta['sta_cn'].decode('hex') + ' '
            reply = reply + chnword.telecode.decode('hex') + ':' + everySta['sta_tele'].encode('utf8') + '\n'

        return reply[0:-1]

    def pss(self, emu_no):
        """Search for the information of a EMU train.
        """
        search = depotHook.EMUinfo(int(emu_no))
        return search.form_reply()

    def jks(self):
        """
        Catch all trains in the late-monitor
        :return:
        """
        import subArr
        sub_arr_db = subArr.Table()
        train_db = train.Table()
        train_str_list = sub_arr_db.train_list()
        res_str = "All trains: "
        for every_str in train_str_list:
            train_status, train_detail_raw = train_db.search("train_str", every_str)
            train_detail = train_detail_raw[0]
            if train_status:
                # Form the train class
                if train_detail["train_class"] == 'A':
                    train_detail["train_class"] = ''
                res_str = res_str + train_detail["train_class"]
                # Form the train number
                if train_detail["train_num0"] == train_detail["train_num1"]:
                    res_str += str(train_detail["train_num0"])
                # The train has 2 train numbers.
                else:
                    temp_num = str(train_detail["train_num0"])
                    temp_num1 = str(train_detail["train_num1"])
                    if len(temp_num) != len(temp_num1):
                        res_str += str(train_detail["train_num0"]) +\
                            '/' + str(train_detail["train_num1"])
                    else:
                        temp_num += '/'
                        for char_index in range(len(temp_num1)):
                            if temp_num[char_index] != temp_num1[char_index]:
                                temp_num += temp_num1[char_index]
                        res_str += temp_num
            res_str += ' '
        return res_str

    def was(self, train_num):
        """
        Search for latest actual arrival data of a train.
        Train_num must be in class-num format! (For example: "Z133")
        Reply string will be returned.
        :param train_num:
        :return: String
        """
        train_db = train.Table()
        if train_num[0].upper() in actual_class:
            train_status, train_detail =\
                train_db.search_dual(train_num[0].upper(),
                                     int(train_num[1:5]))
        else:
            train_status, train_detail = \
                train_db.search_dual('A', int(train_num[0:4]))

        if not train_status:
            return chnword.wasTrainNotFound.decode('hex')

        import subArr, actArr

        sub_arr_db = subArr.Table()
        sub_status, sub_detail =\
            sub_arr_db.catch_by_train(train_detail[0]["train_str"])

        if not sub_status:
            return chnword.wasSubArrNotAdded.decode('hex')

        act_arr_db = actArr.Table()
        arrival_db = arrival.Table()
        station_db = staInfo.Table()
        res_str = ""
        for every_sub in sub_detail:
            arrival_status, arrival_detail =\
                arrival_db.search_by_id(every_sub["arrival_id"])
            station_status, station_detail =\
                station_db.search("sta_tele", arrival_detail[0]["sta_tele"])
            res_str += station_detail[0]["sta_cn"].decode("hex")
            res_str += ' '*((6-len(station_detail[0]["sta_cn"])/6)*2)

            act_arr_status, act_arr_detail =\
                act_arr_db.search_latest(every_sub["sub_arr_id"])
            if act_arr_status:
                res_str += chnword.wasSchArr.decode('hex')
                res_str += tool.int2str(act_arr_detail["schedule_time"])
                res_str += ' '
                res_str += act_arr_detail["schedule_date"].strftime('%Y-%m-%d')
                res_str += chnword.wasActArr.decode('hex')
                actual_time = act_arr_detail["schedule_time"] +\
                    act_arr_detail["delay"]
                # Correct actual arrival time.
                if actual_time >= 1440:
                    actual_time -= 1440
                if actual_time < 0:
                    actual_time += 1440
                res_str += tool.int2str(actual_time)
                res_str += '\n'
            else:
                res_str += chnword.wasActNoData.decode('hex')
        return res_str

    def wzs(self, train_num, station):
        """
        Get Actual Arrival data of specified train and station.
        :param train_num: String
        :param station: String
        :return:
        """
        print("parse/hlsearch.py: Debug: station:" +
              " {}".format(station.encode('hex')))
        train_db = train.Table()
        if train_num[0].upper() in actual_class:
            train_status, train_detail =\
                train_db.search_dual(train_num[0].upper(),
                                     int(train_num[1:5]))
        else:
            train_status, train_detail = \
                train_db.search_dual('A', int(train_num[0:4]))

        if not train_status:
            return chnword.wzsTrainNotFound.decode('hex')

        station_db = staInfo.Table()
        station_status, station_detail = \
            station_db.search("sta_cn", station.encode('hex'))
        if not station_status:
            return chnword.wzsStationNotExist.decode('hex')

        # Search for Sub-Arr.
        import subArr
        sub_arr_db = subArr.Table()
        sub_arr_status, sub_arr_list = \
            sub_arr_db.catch_by_train(train_detail[0]["train_str"])
        sub_has_station = 0
        the_sub_arr_id = 0
        for every_sub_arr in sub_arr_list:
            if station_detail[0]["sta_tele"] == every_sub_arr["sta_tele"]:
                the_sub_arr_id = every_sub_arr["sub_arr_id"]
                sub_has_station = 1
                break
        if not sub_has_station:
            return chnword.wzsStationNotInSub.decode('hex')

        # Search for the Act-Arr.
        import actArr
        act_arr_db = actArr.Table()
        act_arr_status, act_arr_detail = act_arr_db.search(the_sub_arr_id)
        if not act_arr_status:
            return station + chnword.wzsArrNoData.decode('hex')

        # Format the reply.
        res_str = chnword.wzsTrainNumber.decode('hex') +\
            train_num +\
            ' ' +\
            chnword.wzsStation.decode('hex') +\
            station
        for every_act_arr in act_arr_detail:
            actual_time = every_act_arr["schedule_time"] + \
                          every_act_arr["delay"]
            # Correct actual arrival time.
            if actual_time >= 1440:
                actual_time -= 1440
            if actual_time < 0:
                actual_time += 1440
            res_str += '\n' +\
                every_act_arr["schedule_date"].strftime("%Y-%m-%d") +\
                chnword.wzsScheduleTime.decode('hex') +\
                tool.int2str(every_act_arr["schedule_time"]) +\
                ' ' +\
                chnword.wzsActualTime.decode('hex') +\
                tool.int2str(actual_time)

        return res_str


def test():
    import sys
    test_object = Hls()
    if sys.argv > 1:
        action_name = sys.argv[1]
        action_parameter = sys.argv[2]
        if action_name == 'seq' or action_name == 's':
            # No need to transfer train_num into integer format.
            print(test_object.seqs(action_parameter[1:], action_parameter[0]))
        elif action_name == 'arr' or action_name == 'a':
            print(test_object.arrs(action_parameter[1:], action_parameter[0]))
        elif action_name == 'dbs' or action_name == 'd':
            print(test_object.dbs(action_parameter))
        else:
            print('hlsearch.py: Info: Test ended because of wrong parameter.')
    else:
        print('hlsearch.py: Info: Test ended with nothing happened.')


if __name__ == "__main__":
    test()
