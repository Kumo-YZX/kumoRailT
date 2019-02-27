# Module Name: Arrival #
# Function: Recode a arrival in ARRIVAL table. #
# Author: Kumo Lam(https://github.com/Kumo-YZX) #
# Last Edit: Feb/27/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbmaria', '../dbmaria2.py')

from dbmaria import DbBase
import json


class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'arrival')

    def create(self, definition_file='arrival_definition.json'):
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

    def insert(self, train_str, sta_tele, sta_rank, arr_time, arr_date, dep_time, dep_date):
        """Insert a arrival to the table.
           All parameters are required.
        """
        self.insert_data({"train_str": train_str,
                          "sta_tele": sta_tele,
                          "sta_rank": sta_rank,
                          "arr_time": arr_time,
                          "arr_date": arr_date,
                          "dep_time": dep_time,
                          "dep_date": dep_date
                          })

    def insert_dict(self, parameter_dict):
        """Insert data to table directly, using dict directly.
        """
        self.insert_data(parameter_dict)

    def search(self, train_str=None, sta_tele=None):
        """Search for items by its train_str or sta_tele.
           You must choose one or more condition(s) from train_str and sta_tele.
        """
        condition_dict = {}
        if train_str is not None:
            condition_dict['train_str'] = {'judge': '=', 'value': train_str}
        if sta_tele is not None:
            condition_dict['sta_tele'] = {'judge': '=', 'value': sta_tele}

        if len(condition_dict):
            res = self.query_data([condition_dict])
        else:
            res = self.query_data()

        return len(res), res

    def search_by_id(self, arrival_id):
        """
        Search for arrival data by its ID.
        :param arrival_id:
        :return:
        """
        res = self.query_data([{"arrival_id": {"judge": "=", "value": arrival_id}}])
        return len(res), res

    def search_last(self):
        """
        Search for the last item in arrival table.
        Items is sorted by arrivalID.
        NO parameters required.
        """
        res = self.query_data([], orderFactor={'arrival_id': 'DESC'}, amountLimit=1)
        return len(res), res

    def delete(self, train_str=None):
        """Delete a item/items.
           Parameter are not essential, causing all items deleted.
           If provided, the item that train_str matched will be deleted.
        """
        if train_str is None:
            self.delete_data()
        else:
            self.delete_data([{"train_str": {"judge": "=", "value": train_str}}])

        return 1

    def verify_arrival(self, train_str=None):
        """Verify the existence of a item.
           Parameter are not essential, changing the function to void-judgement.
           A json structure like [{'COUNT(1)':amount}] will be returned.
        """
        if train_str is None:
            res = self.verify_existence([])
        else:
            res = self.verify_existence([{"train_str": {"judge": "=", "value": train_str}}])
        return res[0]['COUNT(1)']

    def search_join(self):
        """
        Query for the arrival in Join method.
        """
        res = self.query_join()
        return res


def init():
    obj = Table()
    obj.create()


if __name__ == "__main__":
    init()
