# Module Name: ActArr
# Function: Record the actual status of an arrival.
# Author: Kumo Lam (https://github.com/Kumo-YZX)
# Last Edit: Mar/17/2019 #
#


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbmaria', '../dbmaria2.py')
load_module('arrival', '../dbp4/arrival.py')
load_module('subArr', 'subArr.py')

from dbmaria import DbBase
import arrival, subArr
import json


class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'actArr')

    def create(self, definition_file="actArr_definition.json"):
        """Create an actArr table.
        """
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

    def new(self, sub_arr_id, the_date):
        """add a new log to actArr table with no data.
           sub_arr_id must be a int marking a subArr data, or an error will be raised.
           The date must be a date object.
        """
        import datetime
        sub_arr_db = subArr.Table()
        sub_arr_status, sub_arr_info = sub_arr_db.search_by_id(sub_arr_id)
        schedule_date = the_date +\
                        datetime.timedelta(days=sub_arr_info[0]["schedule_date"]-1)
        if sub_arr_status:
            self.insert_data({"sub_arr_id": sub_arr_id,
                              "schedule_date": schedule_date.strftime("%Y-%m-%d"),
                              "schedule_time": sub_arr_info[0]["schedule_time"],
                              "delay": 0,
                              "query_mark": 0})
        else:
            raise IndexError('subArr do not exist!')

    def verify(self):
        """
        Verify if today's log table is created.
        The amount of today's logs will be returned.
        :return: Integer
        """
        import datetime
        date_today = datetime.datetime.today().strftime("%Y-%m-%d")
        res = self.verify_existence([{"schedule_date": date_today}])
        return res[0]['COUNT(1)']

    def catch(self, the_date, the_time):
        """Get void log with a specified date and a up(no more than) limit time.
           the_date must be a date object.
           the_time must be a integer.
        """
        catch_info = self.query_data([{"schedule_date":
                                       {"judge": '=', "value": the_date.strftime("%Y-%m-%d")},
                                       "schedule_time":
                                       {"judge": '<=', "value": the_time},
                                       "query_mark": {"judge": '=', "value": 0}}])
        return len(catch_info), catch_info

    def write(self, act_arr_id, delay, update_mark=0):
        """Write data to an unmarked log.
           The act_arr_id parameter must be a int marking an existing log.
           The update_mark parameter should be 1 if you want to finish monitoring.
           The delay parameter marks the delay time (minus means train is ahead of time.)
        """
        if update_mark:
            self.update_data({"query_mark": 1, "delay": delay},
                             [{"act_arr_id": {"judge": '=', "value": act_arr_id}}])
        else:
            self.update_data({"delay": delay},
                             [{"act_arr_id": {"judge": '=', "value": act_arr_id}}])

    def search(self, sub_arr_id):
        """Search for details of a sheet of actArr.
           sub_arr_id must be a int.
        """
        search_info = self.query_data([{"sub_arr_id": {"judge": '=', "value": sub_arr_id}}])
        return len(search_info), search_info


def initialize():
    act_arr_obj = Table()
    act_arr_obj.create()


def test():
    import datetime
    act_arr_obj = Table()
    day_today = datetime.datetime.today()
    day_after_tomorrow = day_today + datetime.timedelta(days=2)
    act_arr_obj.new(3, day_today)
    act_arr_obj.new(5, day_today)
    act_arr_obj.new(3, day_today + datetime.timedelta(days=2))
    act_arr_obj.new(5, day_today + datetime.timedelta(days=2))

    print(act_arr_obj.search(3))
    print(act_arr_obj.search(5))

    print(act_arr_obj.catch(day_today, 1440))
    print(act_arr_obj.catch(day_after_tomorrow, 1440))

    act_arr_obj.write(1, 8, 1)
    print(act_arr_obj.catch(day_today, 1440))
    print(act_arr_obj.search(3))
    print(act_arr_obj.search(5))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test()
    else:
        initialize()
