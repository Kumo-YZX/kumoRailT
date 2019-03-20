# Module Name: SubArr #
# Function: Create SubArr set for monitor process. #
# Author: Kumo Lam (https://github.com/Kumo-YZX)#
# Last Edit: Mar/17/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbmaria', '../dbmaria2.py')
load_module('arrival', '../dbp4/arrival.py')

from dbmaria import DbBase
import arrival
import json


class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'subArr')

    def create(self, definition_file='subArr_definition.json'):
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

    def import_arr(self, arrival_id, category=0):
        """Copy a arrival data to subArr table.
           category marks departure(1)/arrival(0).
        """
        arrival_obj = arrival.Table()
        arrival_status, arrival_info = arrival_obj.search_by_id(arrival_id)
        if arrival_status:
            if category:
                self.insert_data({"arrival_id": arrival_info[0]["arrival_id"],
                                  "sta_tele": arrival_info[0]["sta_tele"],
                                  "sta_rank": arrival_info[0]["sta_rank"],
                                  "category": 1,
                                  "schedule_date": arrival_info[0]["dep_date"],
                                  "schedule_time": arrival_info[0]["dep_time"],
                                  "train_str": arrival_info[0]["train_str"],
                                  "status": 1})
            else:
                self.insert_data({"arrival_id": arrival_info[0]["arrival_id"],
                                  "sta_tele": arrival_info[0]["sta_tele"],
                                  "sta_rank": arrival_info[0]["sta_rank"],
                                  "category": 0,
                                  "schedule_date": arrival_info[0]["arr_date"],
                                  "schedule_time": arrival_info[0]["arr_time"],
                                  "train_str": arrival_info[0]["train_str"],
                                  "status": 1})

    def unable(self, train_str):
        """Set status to 0 so that it will not be monitored.
        """
        self.update_data({"status": 0},
                         [{"train_str": {"judge": '=', "value": train_str}}])

    def catch(self, need_status=1, amount_limit=None):
        """Query for all effective subArrs, only sub_arr_id returned.
           The need_status parameter decides whether useless subArr will be returned.
           Only the ID column will be returned as list of dicts with key: sub_arr_id.
        :param need_status: Bool
        :param amount_limit: Integer
        :return: Integer, List
        """
        if need_status:
            query_info = self.query_data([{"status": {"judge": '=', "value": 1}}],
                                         column_list=["sub_arr_id"],
                                         amount_limit=amount_limit)
        else:
            query_info = self.query_data(column_list=["sub_arr_id"],
                                         amount_limit=amount_limit)
        return len(query_info), query_info

    def catch_by_train(self, train_str, need_status=1, amount_limit=None):
        """
        Catch specified sub_arr marked by their train_str.
        Amount of sub_arr and the list contains all sub_arr_id will be returned.
        Return value will be a list of dicts with key: sub_arr_id.
        :param train_str: String
        :param need_status: Bool
        :param amount_limit: Integer
        :return: Integer, List
        """
        if need_status:
            query_info = self.query_data([{"status": {"judge": "=", "value": 1},
                                          "train_str": {"judge": "=", "value": train_str}}],
                                         column_list=["sub_arr_id", "arrival_id"],
                                         order_factor="sta_rank desc",
                                         amount_limit=amount_limit)
        else:
            query_info = self.query_data([{"train_str": {"judge": "=", "value": train_str}}],
                                         column_list=["sub_arr_id", "arrival_id"],
                                         order_factor="sta_rank desc",
                                         amount_limit=amount_limit)
        return len(query_info), query_info

    def train_list(self, need_status=1):
        """
        Get train_str parameter of every arrival.
        A list contains all train_str will be returned.
        If need_status is set to 1, useless arrivals will be ignored.
        :param: need_status: Integer
        :return: List
        """
        if need_status:
            query_info = self.query_data([{"status": {"judge": '=', "value": 1}}],
                                         column_list=["train_str"])
        else:
            query_info = self.query_data(column_list=["train_str"])
        train_list = []
        for every_arr in query_info:
            if every_arr["train_str"] not in train_list:
                train_list.append(every_arr["train_str"])
        return train_list

    def delete(self, train_str):
        self.delete_data([{"train_str": train_str}])

    def search_by_id(self, sub_arr_id):
        """Search for a subArr data with its Id.
           The sub_arr_id parameter must be an integer.
        """
        arr_info = self.query_data([{"sub_arr_id": {"judge": '=', "value": sub_arr_id}}])
        return len(arr_info), arr_info


def initialize():
    obj = Table()
    obj.create()


def add_by_id():
    arrival_id = int(raw_input("arrival_id: "))
    category_num = int(raw_input("category: "))
    obj = Table()
    obj.import_arr(arrival_id, category_num)


def add_by_train():
    train_str = raw_input("train_str: ")
    category_num = int(raw_input("category(dep:1/arr:0): "))
    import arrival
    arrival_search = arrival.Table()
    arrival_status, arrival_list = arrival_search.search(train_str=train_str)
    if arrival_status:
        arrival_list = arrival_list[1:]
        obj = Table()
        for every_arrival in arrival_list:
            obj.import_arr(every_arrival['arrival_id'], category_num)
            print("dbmaria/dbp5/subArr.py: Info: " +
                  "Import arrival: {}".format(every_arrival['arrival_id']))
    else:
        print("dbmaria/dbp5/subArr.py: Warning: No arrival data found.")


def test():
    obj = Table()
    print(obj.catch())
    obj.unable('001G1001')
    print(obj.catch())

    obj.delete('001G6001')
    print(obj.catch())

    print(obj.search_by_id(2))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'add1':
        add_by_id()
    elif len(sys.argv) > 1 and sys.argv[1] == 'add2':
        add_by_train()
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
         test()
    else:
        initialize()

