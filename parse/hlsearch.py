# Module Name: hlsearch(high-level search) #
# Function: Connect the database and return info to the parse module. #
# Author: Kumo Lam(github.com/Kumo-YZX) #
# Last Edit: Jan/01/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('arrival', '../dbmaria/dbp4/arrival.py')
load_module('staInfo', '../dbmaria/dbp1/staInfo.py')
load_module('trainCode', '../dbmaria/dbp3/trainCode.py')
load_module('train', '../dbmaria/dbp3/train.py')
load_module('seq', '../dbmaria/dbp2/seq.py')
load_module('depot', '../dbmaria/dbp2/depot.py')
load_module('tool', '../tool/tool.py')

import arrival, staInfo, trainCode, train, seq, depot
import tool
import chnword


class Hls(object):

    def __init__(self):
        print('hlsearch.py: Info: High level search loaded.')

    def seqs(self, train_num, train_class):
        """Provide the sequence and department & terminal station of a train.
           Parameter train_num and train_class must be provided.
           train_num can be in any(string/integer) format.
           Return value(Reply) is in Chn format.
        """
        reply = train_class + str(train_num) + ' '
        # Initialize the train/arrival/station table object.
        train_db = train.table()
        arrival_table = arrival.table()
        sta_table = staInfo.table()
        # Search for the train.
        train_status, train_info = train_db.searchDual(train_class, str(train_num))
        if not train_status:
            print('hlseach.py: Warning: This train does not exist.')
            return reply + chnword.trainDoNotExist.decode('hex')
        train_status, arr_info = arrival_table.search(train_info[0]['trainStr'])
        if not train_status:
            return chnword.trainExistsButNoArrival.decode('hex')
        # Search for the dep & arr station of this train.
        first_status, first_info = sta_table.search('staTele', arr_info[0]['staTele'])
        last_status, last_info = sta_table.search('staTele', arr_info[-1]['staTele'])
        reply = reply + first_info[0]['staCn'].decode('hex') + '-' + last_info[0]['staCn'].decode('hex') + '\n'
        del train_status, first_status, last_status, arr_info
        del arrival_table, sta_table
        # Initialize the sequence/depot table object.
        seq_db = seq.table()
        depot_db = depot.table()
        # Search for the depot & sequence data.
        seq_status, seq_info = seq_db.search('seqID', train_info[0]['seqId'])
        reply = reply + chnword.EMUType.decode('hex') + ':' + seq_info[0]['emuType'].decode('hex') + '\n'
        staff_status, staff_info = depot_db.search(int(seq_info[0]['staff']))
        vehicle_status, vehicle_info = depot_db.search(int(seq_info[0]['depot']))
        reply = reply + staff_info[0]['depotCn'].decode('hex') + chnword.staffDep.decode('hex') + ' '
        reply = reply + vehicle_info[0]['depotCn'].decode('hex') + chnword.vehicleDep.decode('hex') + '\n'
        del staff_status, staff_info, vehicle_status, vehicle_info
        seq_search_status, seq_search_trains = train_db.search('seqId', train_info[0]['seqId'])
        del seq_search_status, seq_status
        from operator import itemgetter
        reply = reply + chnword.seqNo.decode('hex') + ':'
        # Sort the trains in the same sequence and format the reply.
        seq_search_trains = sorted(seq_search_trains, key=itemgetter('seqRank'))
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
        train_db = train.table()
        arrival_db = arrival.table()
        station_db = staInfo.table()
        # Search for train data.
        train_status, train_info = train_db.searchDual(train_class, int(train_num))
        if not train_status:
            print('hlseach.py: Warning: This train does not exist.')
            return chnword.trainDoNotExist.decode('hex')
        reply = chnword.trainNo.decode('hex') + ':' + train_class + str(train_num) + '\n'
        # Search for all the arrivals.
        train_status, arr_info = arrival_db.search(train_info[0]['trainStr'])
        if not train_status:
            return chnword.trainExistsButNoArrival.decode('hex')
        del train_status
        # Format them.
        for everyArr in arr_info:
            station_status, station_info = station_db.search('staTele', everyArr['staTele'])
            reply = reply + station_info[0]['staCn'].decode('hex') + (8-len(station_info[0]['staCn'])/3)*' '
            if everyArr['arrTime'] == 1441:
                reply = reply + '-----' + ' '
            else:
                reply = reply + tool.int2str(everyArr['arrTime']) + ' '

            if everyArr['depTime'] == 1441:
                reply = reply + '-----' + '\n'
            else:
                reply = reply + tool.int2str(everyArr['depTime']) + '\n'
        del station_status

        return reply[0:-1]

    def dbs(self, sta_pinyin):
        """Search for the telecode of a station.
           Parameter sta_pinyin is the first character of the station's pinyin.
        """
        station_db = staInfo.table()
        station_status, station_info = station_db.search('sta_pinyin', sta_pinyin.lower())
        if not station_status:
            print('hlseach.py: Warning: This station does not exist.')
            return chnword.stationDoNotExist.decode('hex')
        reply = ''
        for everySta in station_info:
            reply = reply + chnword.telecode.decode('hex') + ':' + everySta['staTele'].encode('utf8') + ' '
            reply = reply + chnword.station.decode('hex') + ':' + everySta['staCn'].decode('hex') + '\n'

        return reply[0:-1]

    def pss(self, emu_no):
        """Search for the infomation of a EMU train.
           Not avilable yet now.
        """
        print(tool.processEmuno(str(emu_no)))
        return tool.processEmuno(str(emu_no))


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
