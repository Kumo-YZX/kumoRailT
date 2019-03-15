# Module Name:StaInfo #
# Function: Define database command to control items in STAINFO table. #
# Author: Kumo(https://github.com/user/Kumo-YZX) #
# Last Edit: Jan/26/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbmaria', '../dbmaria2.py')

from dbmaria import DbBase
import json


class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'staInfo')

    def create(self, definition_file='staInfo_definition.json'):
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

    def update_all(self):
        """Fill the table with newest data.
           You need to delete old data manually.
           No parameters required.
        """
        import urllib2
        site_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        raw_data = urllib2.urlopen(site_url, timeout=5).read()
        raw_data = raw_data[21:-2]
        all_stations = raw_data.split('@')
        for every_station in all_stations:
            info_split = every_station.split('|')
            self.insert_data({"sta_cn": info_split[1].encode("hex"),
                              "sta_tele": info_split[2],
                              "sta_py": info_split[4],
                              "sta_num": int(info_split[5])})

    def insert(self, parameter_dict):
        """Insert data to table manually.
           Parameter: parameter_dict must be formed in formatted form.
        """
        self.insert_data(parameter_dict)

    def delete(self, key=None, value=None):
        """Delete data.
           Parameters are not essential.
           If provided must be in key-value format that matches table items.
           If not provided, all data in this table will be deleted.
        """
        if key is None:
            self.delete_data([])
        else:
            self.delete_data([{key: value}])

    def search(self, key=None, value=None):
        """Search for data in this table.
           Parameters are not essential.
           If provided, they must be in key-value format that maches table items.
           If not provided, all data will be returned.
           Return value will be in existence-result format with raw items.
        """
        if key is None:
            res = self.query_data()
        else:
            res = self.query_data([{key: value}])
        
        return len(res), res

    def verify(self, key, value):
        """Verify the existence of specified data.
           Parameters: key value are essential.
           The result means both the existence and the amount.
        """
        res = self.verify_existence([{key: value}])
        return res

    def update_sele(self, sta_tele, status=0):
        """Mark the station as special.
           Parameter is the sta_tele of the item.
           Nothing will be returned.
        """
        self.update_data({"sele_sta": status},
                         [{"sta_tele": sta_tele}])

    def verify_special(self, sta_num):
        """Verify the existence of marked special data.
           Amount of this stations(a number) will be returned.
        """
        res = self.verifyExistence([{'sta_num': {'judge': '>=', 'value': sta_num}}])
        return res[0]['COUNT(1)']


if __name__ == "__main__":
    import sys
    obj = Table()
    if sys.argv[1] == 'cre':
        obj.create()
    elif sys.argv[1] == 'upd':
        obj.update_all()
    elif sys.argv[1] == 'del':
        obj.delete()
    else:
        print 'dbmaria/dbp1/staInfo.py: Warning: Unknown command!'
